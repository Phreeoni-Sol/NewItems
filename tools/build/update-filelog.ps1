param([Parameter(Mandatory)][string]$OriginalRoot)
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$original=(Resolve-Path -LiteralPath $OriginalRoot).Path
$log='recon-output/file-log.csv'
$entries=@(foreach($file in Get-ChildItem -LiteralPath $root -Recurse -File|Sort-Object FullName) {
    $relative=[IO.Path]::GetRelativePath($root,$file.FullName).Replace('\','/')
    if($relative -eq $log){continue}
    $source=Join-Path $original $relative
    $hash=(Get-FileHash -LiteralPath $file.FullName).Hash
    $action=if(-not (Test-Path -LiteralPath $source)){'GENERATED'}elseif((Get-FileHash -LiteralPath $source).Hash -eq $hash){'PRESERVED'}else{'MODIFIED'}
    [pscustomobject]@{Action=$action;Path=$relative;SHA256=$hash}
})
foreach($file in Get-ChildItem -LiteralPath $original -Recurse -File) {
    $relative=[IO.Path]::GetRelativePath($original,$file.FullName).Replace('\','/')
    if(-not(Test-Path -LiteralPath (Join-Path $root $relative))){throw "Original handoff file removed: $relative"}
}
$entries|Export-Csv -LiteralPath (Join-Path $root $log) -NoTypeInformation -Encoding utf8
Write-Output "LOG $($entries.Count) project files; original handoff files present. File log excludes itself."
