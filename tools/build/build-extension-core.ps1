param([Parameter(Mandatory)][string]$ScratchRoot,[Parameter(Mandatory)][string]$OutputRoot,[switch]$DryRun)
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$output=[IO.Path]::GetFullPath($OutputRoot)
if(Test-Path -LiteralPath $output){throw 'Output exists: choose a new build directory.'}
if($DryRun){Write-Output 'DRY RUN: build extension library only; no game launch, hooks or IDs registered.';return}
. (Join-Path $PSScriptRoot 'csharp-offline.ps1')
$sources=@((Get-ChildItem -LiteralPath (Join-Path $root 'runtime/ExtensionCore') -Filter '*.cs').FullName)
$compiled=Join-Path ([IO.Path]::GetFullPath($ScratchRoot)) 'ForgottenJobs.ExtensionCore.dll'
Invoke-OfflineCSharp -Sources $sources -Output $compiled -ScratchRoot $ScratchRoot
New-Item -ItemType Directory -Path $output|Out-Null
Copy-Item -LiteralPath $compiled -Destination $output
@{Library='ForgottenJobs.ExtensionCore';Mode='Development library, no Reloaded entrypoint';GameIntegrated=$false;IDAllocated=$false;SHA256=(Get-FileHash -LiteralPath (Join-Path $output 'ForgottenJobs.ExtensionCore.dll')).Hash;Sources=@($sources|ForEach-Object{@{File=[IO.Path]::GetRelativePath($root,$_).Replace('\','/');SHA256=(Get-FileHash -LiteralPath $_).Hash}})}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $output 'build-manifest.json') -Encoding utf8
Write-Output "BUILT extension library: $output. Not an installable playable mod."
