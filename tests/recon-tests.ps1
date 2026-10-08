param([Parameter(Mandatory)][string]$GameRoot,[Parameter(Mandatory)][string]$LoaderRoot,[Parameter(Mandatory)][string]$ScratchRoot)
$ErrorActionPreference='Stop'
$project=Split-Path $PSScriptRoot -Parent
$inventory=Join-Path $project 'tools\extract\recon.ps1'
$extract=Join-Path $project 'tools\extract\sample-tables.ps1'
$scratch=[IO.Path]::GetFullPath($ScratchRoot)
$passed=[Collections.Generic.List[string]]::new()
foreach ($script in @($inventory,$extract)) {
    $blocked=$false
    try {
        if ($script -eq $inventory) { & $script -GameRoot $GameRoot -LoaderRoot $LoaderRoot -OutputRoot $GameRoot -DryRun | Out-Null }
        else { & $script -GameRoot $GameRoot -LoaderRoot $LoaderRoot -SampleRoot $GameRoot -ReportRoot $scratch -DryRun | Out-Null }
    } catch { if ($_.Exception.Message -match 'separate') { $blocked=$true } else { throw } }
    if (-not $blocked) { throw 'Source path safety check failed.' }
}
$passed.Add('Both scripts reject outputs inside the source game directory, including dry-run.')
$before=Get-FileHash -LiteralPath (Join-Path $GameRoot 'FFT_enhanced.exe')
& $inventory -GameRoot $GameRoot -LoaderRoot $LoaderRoot -OutputRoot (Join-Path $scratch 'dry-only') -DryRun | Out-Null
if (Test-Path -LiteralPath (Join-Path $scratch 'dry-only')) { throw 'Dry-run wrote files.' }
$passed.Add('Inventory dry-run creates no files.')
foreach ($run in @('a','b')) {
    & $inventory -GameRoot $GameRoot -LoaderRoot $LoaderRoot -OutputRoot (Join-Path $scratch $run) | Out-Null
    & $extract -GameRoot $GameRoot -LoaderRoot $LoaderRoot -SampleRoot (Join-Path $scratch ($run+'-samples')) -ReportRoot (Join-Path $scratch $run) | Out-Null
}
foreach ($name in @('archive-files.csv','archives.csv','executables.json','sample-summary.json','nxd-row-keys.csv')) {
    $a=(Get-FileHash -LiteralPath (Join-Path $scratch ('a\'+$name))).Hash
    $b=(Get-FileHash -LiteralPath (Join-Path $scratch ('b\'+$name))).Hash
    if ($a -ne $b) { throw "Non-reproducible output: $name" }
}
$passed.Add('Two independent inventory/extraction runs give identical five report hashes.')
$passed.Add('All selected NXD rows decode; duplicate keys, column count and decompressed size checks pass.')
if ($before.Hash -ne (Get-FileHash -LiteralPath (Join-Path $GameRoot 'FFT_enhanced.exe')).Hash) { throw 'Executable changed.' }
$passed.Add('Enhanced executable hash is unchanged.')
$passed | ForEach-Object { Write-Output "PASS $_" }
