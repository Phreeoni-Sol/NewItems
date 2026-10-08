param([Parameter(Mandatory)][string]$IcedDll)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
[void][Reflection.Assembly]::LoadFrom([IO.Path]::GetFullPath($IcedDll))
if(-not ('ConsumerDecoder' -as [type])){Add-Type -Path (Join-Path $root 'tools/extract/ConsumerDecoder.cs') -ReferencedAssemblies @([IO.Path]::GetFullPath($IcedDll),(Join-Path $PSHOME 'ref/System.Collections.dll')) -CompilerOptions '/nowarn:1701'}
$fixture=[byte[]]@(0x83,0xf9,0,0x74,6,0xb8,1,0,0,0,0xc3,0xb8,2,0,0,0,0xc3)
$graph=[ConsumerDecoder]::DecodeReachable($fixture,0x1000)
if(@($graph|Where-Object Mnemonic -eq Ret).Count -ne 2 -or @($graph|Where-Object {$_.Mnemonic -eq 'Mov' -and $_.Operands -match '0x2'}).Count -ne 1){throw 'Conditional branch coverage lost after first RET.'}
'PASS reachable decoder follows both sides of conditional branches and later returns.'
$rejected=$false
try{[void][ConsumerDecoder]::DecodeReachable([byte[]]@(0xeb,0x7f),0x1000)}catch{$rejected=$true}
if(-not $rejected){throw 'Unbounded branch accepted.'}
'PASS branch beyond bounded preview rejected.'
$instruction=[ConsumerDecoder]::Decode([byte[]]@(0xc7,5,0xf6,0,0,0,1,0,0,0),0x1000)[0]
if($instruction.RipTarget -ne 0x1100 -or $instruction.DisplacementOffset -ne 2 -or $instruction.DisplacementSize -ne 4){throw 'Displacement recovery confused a trailing immediate with RIP displacement.'}
'PASS RIP displacement recovered even with a trailing immediate.'
$map=Get-Content -Raw -LiteralPath (Join-Path $root 'recon-output/consumer-map.json')|ConvertFrom-Json
if($map.ConsumerSites.Count -ne 72 -or $map.UnmappedSites.Count -ne 0 -or $map.CoverageApproved){throw 'Consumer evidence changed or was improperly approved.'}
$command=$map.Functions|Where-Object BeginRva -eq 0x275860
if(@($command.Instructions|Where-Object {$_.Address -eq $map.ImageBase+0x275922 -and $_.Mnemonic -eq 'Cmp' -and $_.Operands -match '0xE3'}).Count -ne 1){throw 'Native command route 227 boundary not found.'}
$slot=$map.Functions|Where-Object BeginRva -eq 0x2b8f18
if(-not ($slot.Instructions.Operands -contains 'ECX, 0xA0')){throw 'Job-to-progression-slot mapping evidence changed.'}
'PASS local map: 72 address candidates, command accessor branches and progress-slot mapper recorded; coverage not approved.'
