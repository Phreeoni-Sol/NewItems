param([Parameter(Mandatory)][string]$LoaderRoot,[Parameter(Mandatory)][string]$SampleRoot,[Parameter(Mandatory)][string]$OutputRoot,[int]$JobId=76)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot -Parent) 'build\nxd.ps1')
Initialize-Nxd $LoaderRoot
$job=Read-Nxd (Join-Path $SampleRoot '0004.fr.pac_job.fr.nxd') 'Job'
$ability=Read-Nxd (Join-Path $SampleRoot '0004.fr.pac_ability.fr.nxd') 'Ability'
$commands=Read-Nxd (Join-Path $SampleRoot '0004.fr.pac_jobcommand.fr.nxd') 'JobCommand'
$general=Read-Nxd (Join-Path $SampleRoot '0004.pac_generaljob.nxd') 'GeneralJob'
$commandId=[int](Get-NxdCell $job $JobId 'jobcommand+Id')
[xml]$xml=Get-Content -LiteralPath (Join-Path $LoaderRoot 'TableData\JobCommandData.xml') -Raw
$entry=@($xml.JobCommandTable.Entries.JobCommand | Where-Object {[int]$_.Id -eq $commandId})
if($entry.Count -ne 1){throw 'Command missing/duplicated in loader template.'}
$abilities=foreach($node in $entry[0].ChildNodes) {
    if($node.Name -notmatch '^(AbilityId|ReactionSupportMovementId)\d+$' -or [int]$node.InnerText -eq 0){continue}
    $id=[int]$node.InnerText
    $references=@(foreach($other in $xml.JobCommandTable.Entries.JobCommand){if(@($other.ChildNodes|Where-Object{$_.Name -match '^(AbilityId|ReactionSupportMovementId)\d+$' -and $_.InnerText -eq [string]$id}).Count){[int]$other.Id}})
    [pscustomobject]@{Slot=$node.Name;AbilityId=$id;Name=(Get-NxdCell $ability $id 'Name');JpCostBytes=@((Get-NxdCell $ability $id 'JpCost1'),(Get-NxdCell $ability $id 'JpCost2'));CommandReferences=$references}
}
$result=[pscustomobject]@{JobId=$JobId;JobName=(Get-NxdCell $job $JobId 'Name');CommandId=$commandId;CommandName=(Get-NxdCell $commands $commandId 'Name');VisualType=(Get-NxdCell $job $JobId 'jobtype+Id');PortraitIndex=(Get-NxdCell $job $JobId 'TexturePartsIndex');Abilities=$abilities;GeneralJobRows=$general.Rows.Count;UnusedJobIds='UNKNOWN: absent rows do not imply available storage';SaveMasteryLayout='UNKNOWN';Runtime='NOT_TESTED'}
New-Item -ItemType Directory -Path $OutputRoot -Force|Out-Null
$target=Join-Path $OutputRoot ('job-'+$JobId+'-audit.json')
$result|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $target -Encoding utf8
Write-Output "GENERATED $([IO.Path]::GetFullPath($target))"
$result
