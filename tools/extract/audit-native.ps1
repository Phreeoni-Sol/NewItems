param([Parameter(Mandatory)][string]$Executable,[Parameter(Mandatory)][string]$LoaderRoot,[Parameter(Mandatory)][string]$SignaturesPath,[Parameter(Mandatory)][string]$IcedDll,[Parameter(Mandatory)][string]$OutputRoot)
$ErrorActionPreference='Stop'
$exe=(Resolve-Path -LiteralPath $Executable).Path
$output=[IO.Path]::GetFullPath($OutputRoot).TrimEnd('\')
foreach($source in @((Split-Path $exe -Parent),(Resolve-Path -LiteralPath $LoaderRoot).Path)) {
    if($output.Equals($source,[StringComparison]::OrdinalIgnoreCase) -or $output.StartsWith($source+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Output must be separate from source.'}
}
[void][Reflection.Assembly]::LoadFrom([IO.Path]::GetFullPath($IcedDll))
if(-not ('ForgottenNativeAudit' -as [type])) {Add-Type -Path (Join-Path $PSScriptRoot 'NativeAudit.cs') -ReferencedAssemblies @([IO.Path]::GetFullPath($IcedDll),(Join-Path $PSHOME 'ref\System.Collections.dll')) -CompilerOptions '/nowarn:1701'}
[void][Reflection.Assembly]::LoadFrom((Join-Path $LoaderRoot 'fftivc.utility.modloader.Interfaces.dll'))
$bytes=[IO.File]::ReadAllBytes($exe)
$stream=[IO.File]::OpenRead($exe);$pe=[Reflection.PortableExecutable.PEReader]::new($stream)
try {
    $headers=$pe.PEHeaders;$imageBase=$headers.PEHeader.ImageBase
    $text=@($headers.SectionHeaders|Where-Object Name -eq '.text')[0]
    $code=[byte[]]::new($text.SizeOfRawData)
    [Array]::Copy($bytes,$text.PointerToRawData,$code,0,$code.Length)
    $definitions=@(
        @{Name='JobDataTable';Struct='JOB_DATA';Back=1;Count=176},
        @{Name='JobCommandDataTable';Struct='JOB_COMMAND_DATA';Back=5;Count=176},
        @{Name='JobNeedLevelDataTable';Struct='JOB_NEED_LEVEL_DATA';Back=16;Count=22}
        @{Name='AbilityDataTable';Struct='ABILITY_COMMON_DATA';Back=0;Count=512}
    )
    $results=foreach($definition in $definitions) {
        $line=@(Get-Content -LiteralPath $SignaturesPath|Where-Object{$_ -match ('^'+$definition.Name+'\s*=')})
        if($line.Count -ne 1){throw 'Signature absent/duplicated.'}
        $signature=($line[0] -split '=',2)[1].Trim()
        $matches=[ForgottenNativeAudit]::Matches($bytes,$signature)
        if($matches.Count -ne 1){throw "Signature $($definition.Name) has $($matches.Count) matches."}
        $type=[Type]::GetType("fftivc.utility.modloader.Interfaces.Tables.Structures.$($definition.Struct), fftivc.utility.modloader.Interfaces")
        $size=[Runtime.InteropServices.Marshal]::SizeOf([type]$type)
        $start=$matches[0]-$definition.Back*$size
        $section=@($headers.SectionHeaders|Where-Object{$start -ge $_.PointerToRawData -and $start -lt $_.PointerToRawData+$_.SizeOfRawData})[0]
        $rva=$section.VirtualAddress+$start-$section.PointerToRawData
        $refs=[ForgottenNativeAudit]::References($code,$imageBase+$text.VirtualAddress,$imageBase+$rva,$definition.Count*$size)
        $rows=foreach($id in 0..($definition.Count-1)) {
            $offset=$start+$id*$size
            $data=[byte[]]::new($size);[Array]::Copy($bytes,$offset,$data,0,$size)
            [pscustomobject]@{Id=$id;FileOffset=$offset;Hex=[BitConverter]::ToString($data);AllZero=(@($data|Where-Object{$_ -ne 0}).Count -eq 0)}
        }
        [pscustomobject]@{Name=$definition.Name;Signature=$signature;UniqueMatch=$matches[0];StartFileOffset=$start;StartRva=$rva;EntrySize=$size;LoaderDeclaredCount=$definition.Count;Rows=$rows;RipReferences=$refs;AllocationApproved=$false}
    }
    New-Item -ItemType Directory -Path $output -Force|Out-Null
    $overlaps=@(foreach($a in $results){foreach($b in $results){if($a.Name -eq $b.Name -or $a.StartFileOffset -ge $b.StartFileOffset){continue};$end=$a.StartFileOffset+$a.EntrySize*$a.LoaderDeclaredCount;if($end -gt $b.StartFileOffset){[pscustomobject]@{Table=$a.Name;Intersects=$b.Name;FirstOtherTableByte=$b.StartFileOffset;DeclaredEnd=$end;BytesOverBoundary=$end-$b.StartFileOffset;CompleteRowsBeforeBoundary=[Math]::Floor(($b.StartFileOffset-$a.StartFileOffset)/$a.EntrySize);AllocationApproved=$false}}}})
    foreach($table in $results) {
        $count=$table.LoaderDeclaredCount
        foreach($overlap in $overlaps|Where-Object Table -eq $table.Name){$count=[Math]::Min($count,$overlap.CompleteRowsBeforeBoundary)}
        $table|Add-Member -NotePropertyName NonOverlappingRowCount -NotePropertyValue $count
        $table|Add-Member -NotePropertyName RipReferencesWithinNonOverlappingRange -NotePropertyValue ([ForgottenNativeAudit]::References($code,$imageBase+$text.VirtualAddress,$imageBase+$table.StartRva,$count*$table.EntrySize))
    }
    [pscustomobject]@{ExecutableSHA256=(Get-FileHash -LiteralPath $exe).Hash;SignaturesSHA256=(Get-FileHash -LiteralPath $SignaturesPath).Hash;Tables=$results;Overlaps=$overlaps;Mode='Static read-only';Limit='Counts are loader declarations; unused rows are not automatically allocatable. Linear disassembly may miss indirect accesses or decode embedded data; references are candidates, not a complete relocation map.'}|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $output 'native-table-audit.json') -Encoding utf8
    $results|Select-Object Name,StartFileOffset,StartRva,EntrySize,LoaderDeclaredCount,@{Name='References';Expression={$_.RipReferences.Count}}
} finally {$pe.Dispose();$stream.Dispose()}
