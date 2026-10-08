param([Parameter(Mandatory)][string]$ScratchRoot)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
. (Join-Path $root 'tools/build/csharp-offline.ps1')
$scratch=[IO.Path]::GetFullPath($ScratchRoot)
$assembly=Join-Path $scratch 'ExtensionTests.dll'
$sources=@((Get-ChildItem -LiteralPath (Join-Path $root 'runtime/ExtensionCore') -Filter '*.cs').FullName)+(Join-Path $PSScriptRoot 'extension-core-tests.cs')
Invoke-OfflineCSharp -Sources $sources -Output $assembly -ScratchRoot $scratch -Console
'{"runtimeOptions":{"tfm":"net9.0","framework":{"name":"Microsoft.NETCore.App","version":"9.0.0"}}}'|Set-Content -LiteralPath (Join-Path $scratch 'ExtensionTests.runtimeconfig.json')
& dotnet $assembly (Join-Path $scratch 'sidecar-fixtures')
if($LASTEXITCODE -ne 0){throw 'Extension-core tests failed.'}
