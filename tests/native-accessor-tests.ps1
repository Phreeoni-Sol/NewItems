param([Parameter(Mandatory)][string]$Executable,[Parameter(Mandatory)][string]$ScratchRoot)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
. (Join-Path $root 'tools/build/csharp-offline.ps1')
$scratch=[IO.Path]::GetFullPath($ScratchRoot)
$assembly=Join-Path $scratch 'NativeAccessorTests.dll'
$sources=@((Get-ChildItem -LiteralPath (Join-Path $root 'runtime/ExtensionCore') -Filter '*.cs').FullName)+(Join-Path $PSScriptRoot 'native-accessor-tests.cs')
Invoke-OfflineCSharp -Sources $sources -Output $assembly -ScratchRoot $scratch -Console
'{"runtimeOptions":{"tfm":"net9.0","framework":{"name":"Microsoft.NETCore.App","version":"9.0.0"}}}'|Set-Content -LiteralPath (Join-Path $scratch 'NativeAccessorTests.runtimeconfig.json')
& dotnet $assembly ([IO.Path]::GetFullPath($Executable))
if($LASTEXITCODE -ne 0){throw 'Native accessor fixture tests failed.'}
