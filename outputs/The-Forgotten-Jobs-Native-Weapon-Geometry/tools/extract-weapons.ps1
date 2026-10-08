param(
    [Parameter(Mandatory)][string]$GameRoot,
    [Parameter(Mandatory)][string]$LoaderRoot,
    [Parameter(Mandatory)][string]$SampleRoot,
    [Parameter(Mandatory)][string]$ReportRoot,
    [switch]$DryRun
)
$ErrorActionPreference='Stop'
$game=(Resolve-Path -LiteralPath $GameRoot).Path.TrimEnd('\')
$loader=(Resolve-Path -LiteralPath $LoaderRoot).Path.TrimEnd('\')
$samples=[IO.Path]::GetFullPath($SampleRoot).TrimEnd('\')
$report=[IO.Path]::GetFullPath($ReportRoot).TrimEnd('\')
foreach ($destination in @($samples,$report)) {
    foreach ($source in @($game,$loader)) {
        if ($destination.Equals($source,[StringComparison]::OrdinalIgnoreCase) -or $destination.StartsWith($source+'\',[StringComparison]::OrdinalIgnoreCase) -or $source.StartsWith($destination+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Output paths must be separate from game and loader.' }
    }
}
$selection=@(
 @{Archive='0002.pac';Path='fftpack/unit/battle_wep1_shp.bin';Layout=$null},
 @{Archive='0002.pac';Path='fftpack/unit/battle_wep2_shp.bin';Layout=$null},
 @{Archive='0002.pac';Path='fftpack/unit/battle_wep1_seq.bin';Layout=$null},
 @{Archive='0002.pac';Path='fftpack/unit/battle_wep2_seq.bin';Layout=$null},
 @{Archive='0002.pac';Path='fftpack/unit/battle_wep_spr.bin';Layout=$null}
)
if ($DryRun) { $selection | ForEach-Object { [pscustomobject]$_ }; return }
# Use the game's existing DirectStorage codec; do not install or replace DLLs.
[void][Runtime.InteropServices.NativeLibrary]::Load((Join-Path $game 'dstoragecore.dll'))
[void][Runtime.InteropServices.NativeLibrary]::Load((Join-Path $game 'dstorage.dll'))
foreach ($dll in @('Syroot.BinaryData.Core.dll','Syroot.BinaryData.Memory.dll','Syroot.BinaryData.dll','CommunityToolkit.HighPerformance.dll','System.IO.Hashing.dll','Microsoft.Extensions.Logging.Abstractions.dll','SharpGen.Runtime.dll','SharpGen.Runtime.COM.dll','Vortice.DirectX.dll','Vortice.DirectStorage.dll','FF16Tools.Shared.dll','FF16Tools.Pack.dll','FF16Tools.Files.dll')) { [void][Reflection.Assembly]::LoadFrom((Join-Path $loader $dll)) }
New-Item -ItemType Directory -Path $samples,$report -Force | Out-Null
$summary=[Collections.Generic.List[object]]::new()
$ids=[Collections.Generic.List[object]]::new()
foreach ($item in $selection) {
    $archive=Join-Path $game ('data\enhanced\'+$item.Archive)
    $pack=[FF16Tools.Pack.FF16Pack]::Open($archive,'ffto',$null)
    try {
        $data=$pack.GetFileDataBytes($item.Path)
        if ($data.LongLength -ne $pack.GetFileInfo($item.Path).DecompressedFileSize) { throw "Size mismatch: $($item.Path)" }
        $target=Join-Path $samples ($item.Archive+'_'+[IO.Path]::GetFileName($item.Path))
        [IO.File]::WriteAllBytes($target,$data)
        Write-Output "GENERATED $target"
        $record=[ordered]@{Archive=$item.Archive;Path=$item.Path;Bytes=$data.Length;SHA256=(Get-FileHash -LiteralPath $target).Hash;Header=[BitConverter]::ToString($data,0,[Math]::Min(16,$data.Length));Rows=$null;Type=$null;Category=$null;LayoutInlineSize=$null}
        if ($item.Layout) {
            $nxd=[FF16Tools.Files.Nex.NexDataFile]::FromFile($target)
            $layout=[FF16Tools.Files.Nex.TableMappingReader]::ReadTableLayout($item.Layout,[Version]'1.0.0','ffto')
            $rows=$nxd.RowManager.GetAllRowInfos()
            if (($rows.Key | Sort-Object -Unique).Count -ne $rows.Count) { throw "Duplicate keys: $($item.Path)" }
            $record.Rows=$rows.Count; $record.Type=$nxd.Type.ToString(); $record.Category=$nxd.Category.ToString(); $record.LayoutInlineSize=$layout.TotalInlineSize
            foreach ($row in $rows) {
                # Decode all rows, including variable-length fields; retain only keys in deliverables.
                $values=[FF16Tools.Files.Nex.NexUtils]::ReadRow($layout,$nxd.Buffer,$row.RowDataOffset)
                if ($values.Count -ne $layout.Columns.Count) { throw "Column mismatch: $($item.Path), row $($row.Key)" }
                $ids.Add([pscustomobject]@{Table=$item.Layout;Key=$row.Key;Key2=$row.Key2;Key3=$row.Key3;DataOffset=$row.RowDataOffset})
            }
        }
        $summary.Add([pscustomobject]$record)
    } finally { $pack.Dispose() }
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $report 'sample-summary.json') -Encoding utf8
$ids | Export-Csv -LiteralPath (Join-Path $report 'nxd-row-keys.csv') -NoTypeInformation -Encoding utf8
Write-Output "GENERATED $(Join-Path $report 'sample-summary.json')"
Write-Output "GENERATED $(Join-Path $report 'nxd-row-keys.csv')"
$summary | Format-Table Archive,Path,Bytes,Rows,LayoutInlineSize -AutoSize



