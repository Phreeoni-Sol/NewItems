param([Parameter(Mandatory)][string]$Executable,[Parameter(Mandatory)][string]$IcedDll,[Parameter(Mandatory)][string]$OutputRoot,[uint32[]]$AdditionalRvas=@(0x275860,0x275980,0x2b8f18,0x2b8c44,0x2b8c74,0x28662c))
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$audit=Get-Content -Raw -LiteralPath (Join-Path $root 'recon-output/native-table-audit.json')|ConvertFrom-Json
$exe=(Resolve-Path -LiteralPath $Executable).Path
$output=[IO.Path]::GetFullPath($OutputRoot)
$game=Split-Path $exe -Parent
if($output.Equals($game,[StringComparison]::OrdinalIgnoreCase) -or $output.StartsWith($game+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Separate output required.'}
if((Get-FileHash -LiteralPath $exe).Hash -ne $audit.ExecutableSHA256){throw 'Executable differs from audited build.'}
[void][Reflection.Assembly]::LoadFrom([IO.Path]::GetFullPath($IcedDll))
if(-not ('ConsumerDecoder' -as [type])){Add-Type -Path (Join-Path $PSScriptRoot 'ConsumerDecoder.cs') -ReferencedAssemblies @([IO.Path]::GetFullPath($IcedDll),(Join-Path $PSHOME 'ref/System.Collections.dll')) -CompilerOptions '/nowarn:1701'}
$bytes=[IO.File]::ReadAllBytes($exe)
$stream=[IO.File]::OpenRead($exe);$pe=[Reflection.PortableExecutable.PEReader]::new($stream)
try {
    $headers=$pe.PEHeaders;$base=$headers.PEHeader.ImageBase
    function To-FileOffset([int]$rva) {
        $section=@($headers.SectionHeaders|Where-Object{$rva -ge $_.VirtualAddress -and $rva -lt $_.VirtualAddress+$_.SizeOfRawData})
        if($section.Count -ne 1){throw "RVA not backed by exactly one file section: $rva"}
        return $section[0].PointerToRawData+$rva-$section[0].VirtualAddress
    }
    $exception=$headers.PEHeader.ExceptionTableDirectory
    if($exception.Size % 12 -ne 0){throw 'Unexpected x64 exception directory shape.'}
    $offset=To-FileOffset $exception.RelativeVirtualAddress
    $functions=@(for($entry=0;$entry -lt $exception.Size;$entry+=12){[pscustomobject]@{Begin=[BitConverter]::ToUInt32($bytes,$offset+$entry);End=[BitConverter]::ToUInt32($bytes,$offset+$entry+4);UnwindRva=[BitConverter]::ToUInt32($bytes,$offset+$entry+8)}})
    $text=@($headers.SectionHeaders|Where-Object Name -eq '.text')[0]
    $textBytes=[byte[]]::new($text.SizeOfRawData);[Array]::Copy($bytes,$text.PointerToRawData,$textBytes,0,$textBytes.Length)
    $sites=@(foreach($table in $audit.Tables){foreach($reference in $table.RipReferencesWithinNonOverlappingRange){$parts=$reference.Split('|');[pscustomobject]@{Table=$table.Name;Address=[Convert]::ToUInt64($parts[0],16);Target=[Convert]::ToUInt64($parts[1],16);Kind='RipRelative'}}
        foreach($address in [ConsumerDecoder]::ImageRelativeSites($textBytes,$base+$text.VirtualAddress,$table.StartRva,$table.NonOverlappingRowCount*$table.EntrySize)){[pscustomobject]@{Table=$table.Name;Address=$address;Target=0;Kind='ImageRelativeCandidate'}}
    })
    $groups=@{};$patches=[Collections.Generic.List[object]]::new();$unmapped=[Collections.Generic.List[object]]::new()
    foreach($site in $sites) {
        $rva=$site.Address-$base
        $owners=@($functions|Where-Object{$rva -ge $_.Begin -and $rva -lt $_.End})
        if($owners.Count -ne 1){$unmapped.Add($site);continue}
        $function=$owners[0];$key=[string]$function.Begin
        if(-not $groups.ContainsKey($key)) {
            $file=To-FileOffset $function.Begin
            $code=[byte[]]::new($function.End-$function.Begin);[Array]::Copy($bytes,$file,$code,0,$code.Length)
            $decoded=[ConsumerDecoder]::Decode($code,$base+$function.Begin)
            $groups.Add($key,[pscustomobject]@{BeginRva=$function.Begin;EndRva=$function.End;UnwindRva=$function.UnwindRva;Instructions=$decoded})
        }
        $instruction=@($groups[$key].Instructions|Where-Object Address -eq $site.Address)
        if($instruction.Count -ne 1){throw 'Reference does not agree with function-boundary decoding.'}
        $table=$audit.Tables|Where-Object Name -eq $site.Table
        $i=$instruction[0]
        if($site.Kind -eq 'RipRelative') {
            if($i.RipTarget -ne $site.Target -or $i.DisplacementSize -ne 4){throw 'Invalid RIP relocation site.'}
            $targetOffset=[long]($site.Target-($base+$table.StartRva))
        } else {
            $raw=[byte[]]@($i.Hex.Split('-')|ForEach-Object{[Convert]::ToByte($_,16)})
            $found=@(for($position=1;$position+4 -le $raw.Length;$position++){if([BitConverter]::ToUInt32($raw,$position) -eq $i.MemoryDisplacement){$position}})
            if($found.Count -ne 1){throw 'Image-relative displacement not uniquely recovered.'}
            $i.DisplacementOffset=$found[0];$i.DisplacementSize=4
            $targetOffset=[long]($i.MemoryDisplacement-$table.StartRva)
        }
        $patches.Add([pscustomobject]@{Table=$site.Table;Kind=$site.Kind;InstructionRva=[long]$rva;FunctionBeginRva=$function.Begin;OriginalHex=$i.Hex;InstructionLength=$i.Length;DisplacementOffset=$i.DisplacementOffset;DisplacementSize=4;TargetByteOffset=$targetOffset;MemoryBase=$i.MemoryBase;MemoryIndex=$i.MemoryIndex;Mnemonic=$i.Mnemonic;RuntimeVerified=$false;BaseOriginVerified=($site.Kind -eq 'RipRelative')})
    }
    foreach($rva in $AdditionalRvas) {
        $owners=@($functions|Where-Object{$rva -ge $_.Begin -and $rva -lt $_.End})
        if($owners.Count -eq 0){
            $file=To-FileOffset $rva;$code=[byte[]]::new(512);[Array]::Copy($bytes,$file,$code,0,$code.Length)
            $preview=[ConsumerDecoder]::DecodeReachable($code,$base+$rva)
            $groups.Add([string]$rva,[pscustomobject]@{BeginRva=$rva;EndRva=$preview[-1].Address+$preview[-1].Length-$base;UnwindRva=0;BoundaryKind='Unwindless direct-branch reachable graph in bounded preview; indirect targets unknown';Instructions=$preview})
            continue
        }
        if($owners.Count -ne 1){throw "Additional RVA overlaps exception ranges: $rva"}
        $function=$owners[0];$key=[string]$function.Begin
        if(-not $groups.ContainsKey($key)) {
            $file=To-FileOffset $function.Begin;$code=[byte[]]::new($function.End-$function.Begin);[Array]::Copy($bytes,$file,$code,0,$code.Length)
            $groups.Add($key,[pscustomobject]@{BeginRva=$function.Begin;EndRva=$function.End;UnwindRva=$function.UnwindRva;Instructions=[ConsumerDecoder]::Decode($code,$base+$function.Begin)})
        }
    }
    $stillUnmapped=[Collections.Generic.List[object]]::new()
    foreach($site in $unmapped) {
        $matches=@(foreach($group in $groups.Values){foreach($i in $group.Instructions|Where-Object Address -eq $site.Address){[pscustomobject]@{Function=$group;Instruction=$i}}})
        if($matches.Count -ne 1){$stillUnmapped.Add($site);continue}
        $i=$matches[0].Instruction;$table=$audit.Tables|Where-Object Name -eq $site.Table
        $raw=[byte[]]@($i.Hex.Split('-')|ForEach-Object{[Convert]::ToByte($_,16)})
        $found=@(for($position=1;$position+4 -le $raw.Length;$position++){if([BitConverter]::ToUInt32($raw,$position) -eq $i.MemoryDisplacement){$position}})
        if($site.Kind -ne 'ImageRelativeCandidate' -or $found.Count -ne 1){throw 'Unexpected unmapped-site relocation shape.'}
        $patches.Add([pscustomobject]@{Table=$site.Table;Kind=$site.Kind;InstructionRva=[long]($site.Address-$base);FunctionBeginRva=$matches[0].Function.BeginRva;OriginalHex=$i.Hex;InstructionLength=$i.Length;DisplacementOffset=$found[0];DisplacementSize=4;TargetByteOffset=[long]($i.MemoryDisplacement-$table.StartRva);MemoryBase=$i.MemoryBase;MemoryIndex=$i.MemoryIndex;Mnemonic=$i.Mnemonic;RuntimeVerified=$false;BaseOriginVerified=$false})
    }
    $unmapped=$stillUnmapped
    New-Item -ItemType Directory -Force -Path $output|Out-Null
    @{ExecutableSHA256=$audit.ExecutableSHA256;ImageBase=$base;ConsumerSites=$patches.ToArray();UnmappedSites=$unmapped.ToArray();Functions=@($groups.Values|Sort-Object BeginRva);ExceptionBackedFunctionCount=@($groups.Values|Where-Object {$_.UnwindRva -ne 0}).Count;ReachableLeafGraphCount=@($groups.Values|Where-Object {$_.UnwindRva -eq 0}).Count;CoverageApproved=$false;Mode='Static x64 exception-directory decoding plus bounded reachable leaf graphs';Limit='RIP and image-displacement candidates; stored pointers, other computed addresses, base-register origins and bounds remain unverified.'}|ConvertTo-Json -Depth 9|Set-Content -LiteralPath (Join-Path $output 'consumer-map.json') -Encoding utf8
    $lines=foreach($function in $groups.Values|Sort-Object BeginRva){"FUNCTION RVA 0x$($function.BeginRva.ToString('X'))..0x$($function.EndRva.ToString('X'))";foreach($i in $function.Instructions){'0x{0:X}: {1} {2}' -f ($i.Address-$base),$i.Mnemonic,$i.Operands};''}
    $lines|Set-Content -LiteralPath (Join-Path $output 'consumer-disassembly.txt') -Encoding utf8
    Write-Output "Mapped $($patches.Count) address references in $($groups.Count) exception-backed ranges/reachable leaf graphs; $($unmapped.Count) unmapped. Coverage not approved."
} finally {$pe.Dispose();$stream.Dispose()}
