function Invoke-OfflineCSharp {
    param([string[]]$Sources,[string]$InterfacesDll,[string]$Output,[string]$ScratchRoot,[string]$Manifest,[switch]$Console)
    $dotnet=Split-Path (Get-Command dotnet -ErrorAction Stop).Source -Parent
    $compiler=Get-ChildItem -Path (Join-Path $dotnet 'sdk/*/Roslyn/bincore/csc.dll')|Sort-Object FullName -Descending|Select-Object -First 1
    $references=Get-ChildItem -Path (Join-Path $dotnet 'packs/Microsoft.NETCore.App.Ref/9.*/ref/net9.0/*.dll')|Group-Object DirectoryName|Sort-Object Name -Descending|Select-Object -First 1
    if(-not $compiler -or -not $references){throw '.NET SDK and .NET 9 reference pack required locally.'}
    New-Item -ItemType Directory -Force -Path (Split-Path $Output -Parent),$ScratchRoot|Out-Null
    $arguments=@('/nologo','/nullable:enable','/langversion:latest','/deterministic+','/optimize+',('/target:'+$(if($Console){'exe'}else{'library'})),('/out:"'+$Output+'"'))
    $arguments+=@($references.Group|ForEach-Object{'/reference:"'+$_.FullName+'"'})
    if($InterfacesDll){$arguments+=('/reference:"'+[IO.Path]::GetFullPath($InterfacesDll)+'"')}
    if($Manifest){$arguments+=('/resource:"'+[IO.Path]::GetFullPath($Manifest)+'",probe-manifest.json')}
    $arguments+=@($Sources|ForEach-Object{'"'+[IO.Path]::GetFullPath($_)+'"'})
    $response=Join-Path $ScratchRoot 'compiler.rsp'
    $arguments|Set-Content -LiteralPath $response -Encoding utf8
    & dotnet $compiler.FullName "@$response"
    if($LASTEXITCODE -ne 0){throw 'Offline C# compilation failed.'}
}
