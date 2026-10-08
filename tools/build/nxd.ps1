Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
function Initialize-Nxd([string]$LoaderRoot) {
    foreach ($name in @('Syroot.BinaryData.Core.dll','Syroot.BinaryData.Memory.dll','Syroot.BinaryData.dll','CommunityToolkit.HighPerformance.dll','System.IO.Hashing.dll','Microsoft.Extensions.Logging.Abstractions.dll','FF16Tools.Shared.dll','FF16Tools.Pack.dll','FF16Tools.Files.dll')) {
        [void][Reflection.Assembly]::LoadFrom((Join-Path $LoaderRoot $name))
    }
}
function Read-Nxd([string]$Path,[string]$Table) {
    $file=[FF16Tools.Files.Nex.NexDataFile]::FromFile([IO.Path]::GetFullPath($Path))
    $layout=[FF16Tools.Files.Nex.TableMappingReader]::ReadTableLayout($Table,[Version]'1.0.0','ffto')
    $rows=[Collections.Generic.Dictionary[uint32,object]]::new()
    foreach ($info in $file.RowManager.GetAllRowInfos()) {
        if ($info.Key2 -ne 0 -or $info.Key3 -ne 0) { throw 'Only single-keyed tables are supported.' }
        $cells=[FF16Tools.Files.Nex.NexUtils]::ReadRow($layout,$file.Buffer,$info.RowDataOffset)
        $rows.Add($info.Key,$cells)
    }
    return [pscustomobject]@{Layout=$layout;Rows=$rows;Version=$file.Version}
}
function Set-NxdCell($Table,[uint32]$Id,[string]$Column,$Value) {
    if (-not $Table.Rows.ContainsKey($Id)) { throw "Unknown row ID: $Id" }
    $columns=@($Table.Layout.Columns.Keys)
    $index=[Array]::IndexOf($columns,$Column)
    if ($index -lt 0) { throw "Unknown column: $Column" }
    $old=$Table.Rows[$Id][$index]
    if ($null -ne $old -and $null -ne $Value) { $Value=[Convert]::ChangeType($Value,$old.GetType(),[Globalization.CultureInfo]::InvariantCulture) }
    $Table.Rows[$Id][$index]=$Value
}
function Get-NxdCell($Table,[uint32]$Id,[string]$Column) {
    if (-not $Table.Rows.ContainsKey($Id)) { throw "Unknown row ID: $Id" }
    $index=[Array]::IndexOf(@($Table.Layout.Columns.Keys),$Column)
    if ($index -lt 0) { throw "Unknown column: $Column" }
    return ,$Table.Rows[$Id][$index]
}
function Write-Nxd($Table,[string]$Path) {
    $builder=[FF16Tools.Files.Nex.NexDataFileBuilder]::new($Table.Layout,$null)
    foreach ($id in ($Table.Rows.Keys | Sort-Object)) {
        if (-not $builder.AddRow($id,0,0,$Table.Rows[$id],$false)) { throw "Duplicate ID: $id" }
    }
    $stream=[IO.MemoryStream]::new()
    try { $builder.Write($stream); $data=$stream.ToArray() } finally { $stream.Dispose() }
    $parent=Split-Path ([IO.Path]::GetFullPath($Path)) -Parent
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    [IO.File]::WriteAllBytes([IO.Path]::GetFullPath($Path),$data)
    Write-Host "GENERATED $([IO.Path]::GetFullPath($Path))"
}
function Assert-NxdEqual($Expected,$Actual,[string[]]$AllowedChanges=@()) {
    if ($Expected.Rows.Count -ne $Actual.Rows.Count) { throw 'Row count changed.' }
    $columns=@($Expected.Layout.Columns.Keys)
    foreach ($id in $Expected.Rows.Keys) {
        if (-not $Actual.Rows.ContainsKey($id)) { throw "Missing row: $id" }
        for ($i=0;$i -lt $columns.Count;$i++) {
            $address="$id/$($columns[$i])"
            if ($address -in $AllowedChanges) { continue }
            $a=ConvertTo-Json -InputObject $Expected.Rows[$id][$i] -Depth 12 -Compress
            $b=ConvertTo-Json -InputObject $Actual.Rows[$id][$i] -Depth 12 -Compress
            if ($a -cne $b) { throw "Unexpected cell change: $address ($a -> $b)" }
        }
    }
}
function Add-NxdRowClone($Table,[uint32]$SourceId,[uint32]$NewId) {
    if(-not $Table.Rows.ContainsKey($SourceId)) {throw "Unknown source ID: $SourceId"}
    if($Table.Rows.ContainsKey($NewId)) {throw "ID collision: $NewId"}
    $cells=[Collections.Generic.List[object]]::new()
    foreach($cell in $Table.Rows[$SourceId]) {
        if($null -eq $cell -or $cell -is [string] -or $cell.GetType().IsValueType) {$cells.Add($cell)}
        elseif($cell -is [Array] -and ($cell.GetType().GetElementType().IsValueType -or $cell.GetType().GetElementType() -eq [string])) {$cells.Add($cell.Clone())}
        else {throw 'Cloning reference-based/custom-struct columns is not supported.'}
    }
    $Table.Rows.Add($NewId,$cells)
}
function Assert-NxdPreservesOriginal($Original,$Expanded,[uint32[]]$AddedIds) {
    if(@($AddedIds|Sort-Object -Unique).Count -ne $AddedIds.Count){throw 'Duplicate additions.'}
    if($Expanded.Rows.Count -ne $Original.Rows.Count+$AddedIds.Count){throw 'Unplanned row additions/removals.'}
    foreach($id in $AddedIds){if($Original.Rows.ContainsKey($id) -or -not $Expanded.Rows.ContainsKey($id)){throw 'Addition collides or is missing.'}}
    $columns=@($Original.Layout.Columns.Keys)
    if(($columns -join '|') -cne (@($Expanded.Layout.Columns.Keys)-join '|')){throw 'Schema changed.'}
    foreach($id in $Original.Rows.Keys) {
        if(-not $Expanded.Rows.ContainsKey($id)){throw "Vanilla row removed: $id"}
        for($i=0;$i -lt $columns.Count;$i++) {
            $a=ConvertTo-Json -InputObject $Original.Rows[$id][$i] -Depth 12 -Compress
            $b=ConvertTo-Json -InputObject $Expanded.Rows[$id][$i] -Depth 12 -Compress
            if($a -cne $b){throw "Vanilla cell changed: $id/$($columns[$i])"}
        }
    }
}
