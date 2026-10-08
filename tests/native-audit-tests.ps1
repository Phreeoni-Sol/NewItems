param([Parameter(Mandatory)][string]$IcedDll,[Parameter(Mandatory)][string]$AuditPath)
$ErrorActionPreference='Stop'
$project=Split-Path $PSScriptRoot -Parent
[void][Reflection.Assembly]::LoadFrom([IO.Path]::GetFullPath($IcedDll))
if(-not ('ForgottenNativeAudit' -as [type])){Add-Type -Path (Join-Path $project 'tools/extract/NativeAudit.cs') -ReferencedAssemblies @([IO.Path]::GetFullPath($IcedDll),(Join-Path $PSHOME 'ref/System.Collections.dll')) -CompilerOptions '/nowarn:1701'}
$hits=[ForgottenNativeAudit]::Matches([byte[]]@(0x48,0x01,0x90,0x48,0x02,0x90),'48 ?? 90')
if(($hits -join ',') -ne '0,3'){throw 'Wildcard match failure.'}
foreach($bad in @('','100','GG')) {
    $rejected=$false
    try{[void][ForgottenNativeAudit]::Matches([byte[]]@(1,2),$bad)}catch{$rejected=$true}
    if(-not $rejected){throw 'Invalid signature accepted.'}
}
Write-Output 'PASS wildcard signature scanning and malformed signatures rejected.'
# LEA RAX,[RIP+9] at 0x1000 targets 0x1010; two NOPs complete fixture.
$refs=[ForgottenNativeAudit]::References([byte[]]@(0x48,0x8d,0x05,9,0,0,0,0x90,0x90),0x1000,0x1010,1)
if($refs.Count -ne 1 -or $refs[0] -notmatch '0000000000001010\|Lea'){throw 'RIP target decoding failure.'}
if([ForgottenNativeAudit]::References([byte[]]@(0x48,0x8d,0x05,9,0,0,0),0x1000,0x1011,1).Count -ne 0){throw 'Exclusive reference range failed.'}
Write-Output 'PASS RIP target calculation and exclusive range boundaries.'
$audit=Get-Content -Raw -LiteralPath $AuditPath|ConvertFrom-Json
$job=$audit.Tables|Where-Object Name -eq JobDataTable
$ability=$audit.Tables|Where-Object Name -eq AbilityDataTable
$overlap=$audit.Overlaps|Where-Object Table -eq JobDataTable
if($job.EntrySize -ne 49 -or $overlap.CompleteRowsBeforeBoundary -ne 174 -or $overlap.BytesOverBoundary -ne 96 -or $job.NonOverlappingRowCount -ne 174){throw 'Unexpected local native-table boundary: re-investigate this build.'}
if($job.StartFileOffset+174*49+2 -ne $ability.StartFileOffset){throw 'Job/ability adjacency evidence changed.'}
if(@($audit.Tables|Where-Object AllocationApproved).Count -ne 0){throw 'Audit allocated an engine ID.'}
Write-Output 'PASS local collision evidence: 174 complete Job rows, 2 padding bytes, then Ability; no ID allocated.'
