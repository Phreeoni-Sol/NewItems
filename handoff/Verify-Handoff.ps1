param([string]$ManifestPath=(Join-Path $PSScriptRoot 'integrity-manifest.json'))
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent)).TrimEnd([IO.Path]::DirectorySeparatorChar)
$manifest=Get-Content -LiteralPath $ManifestPath -Raw|ConvertFrom-Json
$checked=0
foreach($item in $manifest.Files){
    if([IO.Path]::IsPathRooted($item.Path)){throw "Invalid absolute manifest path: $($item.Path)"}
    $target=[IO.Path]::GetFullPath((Join-Path $root $item.Path))
    if(-not $target.StartsWith($root+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw "Manifest path escapes project: $($item.Path)"}
    $relative=[IO.Path]::GetRelativePath($root,$target)
    $cursor=$root
    foreach($part in $relative.Split([char[]]@('/','\'),[StringSplitOptions]::RemoveEmptyEntries)){
        $cursor=Join-Path $cursor $part
        if(-not(Test-Path -LiteralPath $cursor)){throw "Missing: $($item.Path)"}
        if((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Refusing linked manifest path: $($item.Path)"}
    }
    $file=Get-Item -LiteralPath $target -Force
    if($file.PSIsContainer -or $file.Length -ne $item.Bytes -or (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $item.SHA256){throw "Integrity mismatch: $($item.Path)"}
    $checked++
}
Write-Output "PASS $checked delivered files match SHA256 manifest. This verifies the delivered baseline; subsequent intentional edits change these hashes."
