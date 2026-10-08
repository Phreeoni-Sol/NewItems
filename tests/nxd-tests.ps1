param([Parameter(Mandatory)][string]$LoaderRoot,[Parameter(Mandatory)][string]$SampleRoot,[Parameter(Mandatory)][string]$ScratchRoot)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot -Parent) 'tools\build\nxd.ps1')
Initialize-Nxd $LoaderRoot
foreach ($item in @(@('Job','0004.fr.pac_job.fr.nxd'),@('Ability','0004.fr.pac_ability.fr.nxd'),@('JobCommand','0004.fr.pac_jobcommand.fr.nxd'),@('GeneralJob','0004.pac_generaljob.nxd'),@('OverrideAbilityActionData','0004.pac_overrideabilityactiondata.nxd'))) {
    $table=Read-Nxd (Join-Path $SampleRoot $item[1]) $item[0]
    $target=Join-Path $ScratchRoot ($item[0]+'.nxd')
    Write-Nxd $table $target
    $after=Read-Nxd $target $item[0]
    Assert-NxdEqual $table $after
    Write-Output "PASS semantic round-trip: $($item[0]), $($table.Rows.Count) rows"
}
$job=Read-Nxd (Join-Path $SampleRoot '0004.fr.pac_job.fr.nxd') 'Job'
$base=Read-Nxd (Join-Path $SampleRoot '0004.fr.pac_job.fr.nxd') 'Job'
Set-NxdCell $job 76 'Name' 'Brise-Lame'
Set-NxdCell $job 76 'Description' 'Épreuve de sérialisation — caractères français.'
$target=Join-Path $ScratchRoot 'job-edited.nxd'
Write-Nxd $job $target
$after=Read-Nxd $target 'Job'
Assert-NxdEqual $job $after
Assert-NxdEqual $base $after @('76/Name','76/Description')
Write-Output 'PASS localized text changes survive serialization; all other cells are preserved.'
foreach ($case in @(@(9999,'Name'),@(76,'UnknownMissingColumn'))) {
    $failed=$false
    try { Set-NxdCell $job $case[0] $case[1] 'Invalid' } catch { if ($_.Exception.Message -like 'Unknown*') {$failed=$true} else {throw} }
    if (-not $failed) {throw 'Invalid row/column was accepted.'}
}
Write-Output 'PASS invalid IDs and columns are rejected.'
