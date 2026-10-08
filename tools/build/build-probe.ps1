param([Parameter(Mandatory)][string]$Executable,[Parameter(Mandatory)][string]$InterfacesDll,[Parameter(Mandatory)][string]$ScratchRoot,[Parameter(Mandatory)][string]$OutputRoot,[switch]$DryRun)
$ErrorActionPreference='Stop'
$project=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$audit=Get-Content -Raw -LiteralPath (Join-Path $project 'recon-output/native-table-audit.json')|ConvertFrom-Json
$exe=(Resolve-Path -LiteralPath $Executable).Path
if((Get-FileHash -LiteralPath $exe).Hash -ne $audit.ExecutableSHA256){throw 'Executable differs from audited build.'}
$output=[IO.Path]::GetFullPath($OutputRoot)
$scratch=[IO.Path]::GetFullPath($ScratchRoot)
foreach($target in @($output,$scratch)) {
    foreach($source in @((Split-Path $exe -Parent),(Split-Path (Resolve-Path -LiteralPath $InterfacesDll).Path -Parent))) {
        if($target.Equals($source,[StringComparison]::OrdinalIgnoreCase) -or $target.StartsWith($source+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Build destination must be separate from input binaries.'}
    }
}
if(Test-Path -LiteralPath $output){throw 'Output exists: choose a new package directory.'}
if($DryRun){Write-Output 'DRY RUN: fingerprint matches; build a diagnostic package only. No engine ID allocation or native writes.';return}
New-Item -ItemType Directory -Force -Path $scratch|Out-Null
$bytes=[IO.File]::ReadAllBytes($exe)
$tables=@(foreach($table in $audit.Tables) {
    $count=$table.LoaderDeclaredCount
    foreach($collision in $audit.Overlaps|Where-Object Table -eq $table.Name){$count=[Math]::Min($count,$collision.CompleteRowsBeforeBoundary)}
    $hashes=@(foreach($row in $table.Rows|Select-Object -First $count) {
        $data=[byte[]]::new($table.EntrySize)
        [Array]::Copy($bytes,$row.FileOffset,$data,0,$data.Length)
        if([BitConverter]::ToString($data) -ne $row.Hex){throw 'Audit row differs from source.'}
        [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($data))
    })
    [pscustomobject]@{Name=$table.Name;Rva=$table.StartRva;EntrySize=$table.EntrySize;OriginalRowHashes=$hashes}
})
$manifest=Join-Path $scratch 'probe-manifest.json'
@{ExecutableSHA256=$audit.ExecutableSHA256;Tables=$tables}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath $manifest -Encoding utf8
$build=Join-Path $scratch 'compiled'
. (Join-Path $PSScriptRoot 'csharp-offline.ps1')
Invoke-OfflineCSharp -Sources @((Join-Path $project 'runtime/ReadOnlyProbe/Probe.cs')) -InterfacesDll $InterfacesDll -Output (Join-Path $build 'ForgottenJobs.ReadOnlyProbe.dll') -ScratchRoot $scratch -Manifest $manifest
New-Item -ItemType Directory -Path $output|Out-Null
Copy-Item -LiteralPath (Join-Path $build 'ForgottenJobs.ReadOnlyProbe.dll') -Destination $output
@{ModId='forgottenjobs.diagnostic.readonly';ModName='The Forgotten Jobs - Read-only diagnostic';ModAuthor='The Forgotten Jobs';ModVersion='0.1.0';ModDescription='Diagnostic only; no new job, patches or save access. Requires Reloaded .NET 9.';ModDll='ForgottenJobs.ReadOnlyProbe.dll';ModDependencies=@();OptionalDependencies=@();SupportedAppId=@('fft_enhanced.exe');IsUniversalMod=$false;CanUnload=$true;HasExports=$false;IsLibrary=$false}|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $output 'ModConfig.json') -Encoding utf8
@{Mode='Diagnostic only';GameSHA256=$audit.ExecutableSHA256;ModuleSHA256=(Get-FileHash -LiteralPath (Join-Path $output 'ForgottenJobs.ReadOnlyProbe.dll')).Hash;RuntimeTested=$false;AllocationApproved=$false}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $output 'build-manifest.json') -Encoding utf8
Write-Output "BUILT diagnostic package: $output. Compilation does not prove runtime compatibility."
