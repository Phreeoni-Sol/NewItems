param(
    [Parameter(Mandatory)][string]$GameRoot,
    [Parameter(Mandatory)][string]$LoaderRoot,
    [Parameter(Mandatory)][string]$OutputRoot,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$game = (Resolve-Path -LiteralPath $GameRoot).Path.TrimEnd('\')
$loader = (Resolve-Path -LiteralPath $LoaderRoot).Path.TrimEnd('\')
$output = [IO.Path]::GetFullPath($OutputRoot).TrimEnd('\')
foreach ($source in @($game,$loader)) {
    if ($output.Equals($source,[StringComparison]::OrdinalIgnoreCase) -or
        $output.StartsWith($source+'\',[StringComparison]::OrdinalIgnoreCase) -or
        $source.StartsWith($output+'\',[StringComparison]::OrdinalIgnoreCase)) {
        throw 'OutputRoot must be separate from game and loader directories.'
    }
}
$archives = @(Get-ChildItem -LiteralPath (Join-Path $game 'data') -Recurse -Filter '*.pac' -File | Sort-Object FullName)
if ($archives.Count -eq 0) { throw 'No PAC archives found.' }
if ($DryRun) {
    [pscustomobject]@{GameRoot=$game;LoaderRoot=$loader;OutputRoot=$output;ArchiveCount=$archives.Count;Action='Read archive directories; write inventories only; no game mutation'}
    return
}
foreach ($dll in @('Syroot.BinaryData.Core.dll','Syroot.BinaryData.Memory.dll','Syroot.BinaryData.dll','CommunityToolkit.HighPerformance.dll','System.IO.Hashing.dll','Microsoft.Extensions.Logging.Abstractions.dll','FF16Tools.Shared.dll','FF16Tools.Pack.dll')) {
    [void][Reflection.Assembly]::LoadFrom((Join-Path $loader $dll))
}
New-Item -ItemType Directory -Path $output -Force | Out-Null
$entries = [Collections.Generic.List[object]]::new()
$packs = [Collections.Generic.List[object]]::new()
foreach ($archive in $archives) {
    $relative = [IO.Path]::GetRelativePath($game,$archive.FullName).Replace('\','/')
    $pack = [FF16Tools.Pack.FF16Pack]::Open($archive.FullName,'ffto',$null)
    try {
        $packs.Add([pscustomobject]@{Archive=$relative;Bytes=$archive.Length;Directory=$pack.ArchiveDir;EncryptedHeader=$pack.HeaderEncrypted;UsesChunks=$pack.UsesChunks;Files=$pack.GetNumFiles()})
        foreach ($entry in $pack.Files.GetEnumerator()) {
            $entries.Add([pscustomobject]@{Archive=$relative;Path=$entry.Key;CompressedBytes=$entry.Value.CompressedFileSize;DecompressedBytes=$entry.Value.DecompressedFileSize;Compressed=$entry.Value.IsCompressed;Offset=$entry.Value.DataOffset;CRC32=$entry.Value.CRC32Checksum})
        }
    } finally { $pack.Dispose() }
}
$entries | Sort-Object Archive,Path | Export-Csv -LiteralPath (Join-Path $output 'archive-files.csv') -NoTypeInformation -Encoding utf8
$packs | Export-Csv -LiteralPath (Join-Path $output 'archives.csv') -NoTypeInformation -Encoding utf8
$fingerprints = foreach ($path in @('FFT_enhanced.exe','FFT_classic.exe')) {
    $file = Get-Item -LiteralPath (Join-Path $game $path)
    [pscustomobject]@{File=$path;Bytes=$file.Length;FileVersion=$file.VersionInfo.FileVersion;SHA256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash}
}
$fingerprints | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'executables.json') -Encoding utf8
$metadata = [pscustomobject]@{GameRoot=$game;LoaderRoot=$loader;LoaderVersion=(Get-Content -LiteralPath (Join-Path $loader 'ModConfig.json') -Raw | ConvertFrom-Json).ModVersion;PackLibrarySHA256=(Get-FileHash -LiteralPath (Join-Path $loader 'FF16Tools.Pack.dll')).Hash;ArchiveCount=$packs.Count;EntryCount=$entries.Count;GameMutations=0}
$metadata | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'environment.json') -Encoding utf8
$tables = foreach ($name in @('JobData.xml','AbilityData.xml','JobCommandData.xml','JobNeedLevelData.xml','StatusEffectData.xml','AbilityTypeData.xml','AbilityActionData.xml','MapTrapFormationData.xml')) {
    $path=Join-Path $loader ('TableData\'+$name)
    [xml]$xml=Get-Content -LiteralPath $path -Raw
    [pscustomobject]@{File=$name;SHA256=(Get-FileHash -LiteralPath $path).Hash;Entries=@($xml.DocumentElement.Entries.ChildNodes | Where-Object NodeType -eq Element).Count;IdBoundComment=(Select-String -LiteralPath $path -Pattern 'IMPORTANT 3' | ForEach-Object {$_.Line.Trim()})}
}
$tables | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $output 'loader-table-evidence.json') -Encoding utf8
$layouts = foreach ($name in @('Job','Ability','JobCommand','Item','UiStatusEffect','GeneralJob','OverrideAbilityActionData')) {
    $path=Join-Path $loader ('Nex\Layouts\ffto\'+$name+'.layout')
    [pscustomobject]@{File=$name+'.layout';SHA256=(Get-FileHash -LiteralPath $path).Hash}
}
$layouts | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'layout-evidence.json') -Encoding utf8
Get-ChildItem -LiteralPath $output -File | Sort-Object Name | ForEach-Object {
    Write-Output "GENERATED $($_.FullName)"
}
$metadata
