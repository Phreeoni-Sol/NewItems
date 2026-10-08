param([Parameter(Mandatory)][string]$InterfacesDll,[Parameter(Mandatory)][string]$ScratchRoot)
$ErrorActionPreference='Stop'
$project=Split-Path $PSScriptRoot -Parent
New-Item -ItemType Directory -Force -Path $ScratchRoot|Out-Null
$probe=[Security.SecurityElement]::Escape((Join-Path $project 'runtime/ReadOnlyProbe/Probe.cs'))
$reference=[Security.SecurityElement]::Escape([IO.Path]::GetFullPath($InterfacesDll))
@"
<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net9.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup><ItemGroup><Compile Include="$probe" Link="Probe.cs"/><Reference Include="Reloaded.Mod.Interfaces"><HintPath>$reference</HintPath></Reference></ItemGroup></Project>
"@|Set-Content -LiteralPath (Join-Path $ScratchRoot 'Tests.csproj')
@'
using ForgottenJobs.ReadOnlyProbe;
using System;
using System.Linq;
using System.Security.Cryptography;
string hash = new('A',64);
var bytes = new byte[]{1,2,3,4};
var table = new TableEvidence("Job",100,2,new[]{Convert.ToHexString(SHA256.HashData(bytes[..2])),Convert.ToHexString(SHA256.HashData(bytes[2..]))});
var manifest = new ProbeManifest(hash,new[]{table});
void Reject(Action action, string name) { try { action(); } catch (InvalidOperationException) { Console.WriteLine("PASS "+name); return; } throw new Exception("Unexpected acceptance: "+name); }
ProbeChecks.ValidateManifest(manifest,hash,104);
if(ProbeChecks.Compare(table,bytes).DifferentRows.Length!=0)throw new Exception("Original mismatch");
bytes[2]=99;
if(!ProbeChecks.Compare(table,bytes).DifferentRows.SequenceEqual(new[]{1}))throw new Exception("Mutation not localized");
Console.WriteLine("PASS vanilla snapshot equality and exact changed-row detection");
Reject(()=>ProbeChecks.ValidateManifest(manifest,new string('B',64),104),"unknown executable rejected before reading memory");
Reject(()=>ProbeChecks.ValidateManifest(manifest,hash,103),"out-of-module range rejected");
Reject(()=>ProbeChecks.ValidateManifest(new(hash,new[]{table,table with {Name="Ability",Rva=102}}),hash,200),"overlapping table ranges rejected");
Reject(()=>ProbeChecks.ValidateManifest(new(hash,new[]{table,table}),hash,200),"duplicate table names rejected");
Reject(()=>ProbeChecks.ValidateManifest(new(hash,new[]{table with {EntrySize=0}}),hash,200),"invalid entry size rejected");
Reject(()=>ProbeChecks.Compare(table,new byte[3]),"truncated snapshot rejected");
Console.WriteLine("Offline checks only; startup and VirtualQuery not executed in game.");
'@|Set-Content -LiteralPath (Join-Path $ScratchRoot 'Program.cs')
. (Join-Path $project 'tools/build/csharp-offline.ps1')
$assembly=Join-Path ([IO.Path]::GetFullPath($ScratchRoot)) 'Tests.dll'
Invoke-OfflineCSharp -Sources @((Join-Path $project 'runtime/ReadOnlyProbe/Probe.cs'),(Join-Path $ScratchRoot 'Program.cs')) -InterfacesDll $InterfacesDll -Output $assembly -ScratchRoot $ScratchRoot -Console
Copy-Item -LiteralPath $InterfacesDll -Destination $ScratchRoot -Force
'{"runtimeOptions":{"tfm":"net9.0","framework":{"name":"Microsoft.NETCore.App","version":"9.0.0"}}}'|Set-Content -LiteralPath (Join-Path $ScratchRoot 'Tests.runtimeconfig.json')
& dotnet $assembly
if($LASTEXITCODE -ne 0){throw 'Probe tests failed.'}
