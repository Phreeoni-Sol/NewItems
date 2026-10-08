param([Parameter(Mandatory)][string]$LoaderRoot,[Parameter(Mandatory)][string]$SampleRoot,[Parameter(Mandatory)][string]$ScratchRoot)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot -Parent) 'tools\build\nxd.ps1')
Initialize-Nxd $LoaderRoot
foreach($item in @(@('Job','0004.fr.pac_job.fr.nxd',76),@('JobCommand','0004.fr.pac_jobcommand.fr.nxd',7),@('GeneralJob','0004.pac_generaljob.nxd',1))) {
    $path=Join-Path $SampleRoot $item[1]
    $original=Read-Nxd $path $item[0];$expanded=Read-Nxd $path $item[0]
    # Research fixture only: this is NOT an allocated engine ID.
    $newId=[uint32](($original.Rows.Keys|Measure-Object -Maximum).Maximum+1)
    Add-NxdRowClone $expanded $item[2] $newId
    if($item[0] -eq 'Job' -or $item[0] -eq 'JobCommand'){Set-NxdCell $expanded $newId 'Name' 'TEST ajout indépendant'}
    $target=Join-Path $ScratchRoot ($item[0]+'-expanded.nxd')
    Write-Nxd $expanded $target
    $after=Read-Nxd $target $item[0]
    Assert-NxdEqual $expanded $after
    Assert-NxdPreservesOriginal $original $after @($newId)
    $failed=$false
    try{Add-NxdRowClone $expanded $item[2] $item[2]}catch{if($_.Exception.Message -match 'collision'){$failed=$true}else{throw}}
    if(-not $failed){throw 'Existing ID was reused.'}
    Write-Output "PASS $($item[0]): one fixture row appended; $($original.Rows.Count) vanilla rows unchanged; collisions rejected."
}
$original=Read-Nxd (Join-Path $SampleRoot '0004.fr.pac_job.fr.nxd') 'Job'
$mutated=Read-Nxd (Join-Path $SampleRoot '0004.fr.pac_job.fr.nxd') 'Job'
Set-NxdCell $mutated 76 'Name' 'Forbidden replacement'
$failed=$false
try{Assert-NxdPreservesOriginal $original $mutated @()}catch{if($_.Exception.Message -match 'Vanilla cell changed'){$failed=$true}else{throw}}
if(-not $failed){throw 'Vanilla mutation escaped the preservation check.'}
Write-Output 'PASS existing-job replacement rejected by preservation check.'
Write-Output 'WARNING: codec fixtures validate NXD additions only, not native allocation/menu/save compatibility.'
