param([Parameter(Mandatory)][string]$Executable,[Parameter(Mandatory)][string]$UpstreamRoot,[Parameter(Mandatory)][string]$IcedDll,[Parameter(Mandatory)][string]$OutputRoot)
$ErrorActionPreference='Stop'
$exe=(Resolve-Path -LiteralPath $Executable).Path
$upstream=(Resolve-Path -LiteralPath $UpstreamRoot).Path
$output=[IO.Path]::GetFullPath($OutputRoot)
foreach($source in @((Split-Path $exe -Parent),$upstream)) {
    if($output.Equals($source,[StringComparison]::OrdinalIgnoreCase) -or $output.StartsWith($source+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Separate audit output required.'}
}
[void][Reflection.Assembly]::LoadFrom([IO.Path]::GetFullPath($IcedDll))
if(-not ('ForgottenNativeAudit' -as [type])) {Add-Type -Path (Join-Path $PSScriptRoot 'NativeAudit.cs') -ReferencedAssemblies @([IO.Path]::GetFullPath($IcedDll),(Join-Path $PSHOME 'ref/System.Collections.dll')) -CompilerOptions '/nowarn:1701'}
$source=Join-Path $upstream 'GenericJobs/Mod.cs'
$matches=[regex]::Matches((Get-Content -Raw -LiteralPath $source),'\["(?<name>[^"]+)"\]\s*=\s*\(\s*"(?<pattern>[0-9A-F? ]+)"')
if($matches.Count -eq 0){throw 'No recognized upstream signatures: review source format.'}
$bytes=[IO.File]::ReadAllBytes($exe)
$patterns=@(foreach($match in $matches){$hits=[ForgottenNativeAudit]::Matches($bytes,$match.Groups['pattern'].Value);[pscustomobject]@{Name=$match.Groups['name'].Value;Pattern=$match.Groups['pattern'].Value;Matches=$hits.Count;FileOffsets=$hits;RuntimeVerified=$false}})
$commit=& git -C $upstream rev-parse HEAD
if($LASTEXITCODE -ne 0){throw 'Source provenance unavailable.'}
New-Item -ItemType Directory -Force -Path $output|Out-Null
@{Source='https://github.com/cipherxof/FFTGenericJobs';Commit=$commit;SourceSHA256=(Get-FileHash -LiteralPath $source).Hash;ExecutableSHA256=(Get-FileHash -LiteralPath $exe).Hash;Patterns=$patterns;Mode='Read-only signature scan, no hooks or patches';AllocationApproved=$false}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $output 'menu-signature-audit.json') -Encoding utf8
Write-Output "AUDIT $($patterns.Count) patterns; $(@($patterns|Where-Object Matches -eq 1).Count) unique; runtime unverified."
