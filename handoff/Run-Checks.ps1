param(
    [ValidateSet('Core','Full')][string]$Mode='Core',
    [string]$ConfigPath=(Join-Path $PSScriptRoot 'environment.local.json'),
    [string]$ScratchRoot
)
$ErrorActionPreference='Stop'
if($PSVersionTable.PSVersion.Major -lt 7){throw 'PowerShell 7 or later is required.'}
$root=Split-Path $PSScriptRoot -Parent
if(-not $ScratchRoot){$ScratchRoot=Join-Path $root 'work/claude-checks'}
$run=Join-Path ([IO.Path]::GetFullPath($ScratchRoot)) ((Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')+'-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $run -Force|Out-Null
$shell=(Get-Process -Id $PID).Path
$results=[Collections.Generic.List[object]]::new()
function Invoke-Check([string]$Name,[string]$Script,[string[]]$Arguments){
    $log=Join-Path $run ($Name+'.log')
    Write-Host "CHECK $Name"
    & $shell -NoProfile -File (Join-Path $root $Script) @Arguments *> $log
    $code=$LASTEXITCODE
    $results.Add([pscustomobject]@{Name=$Name;ExitCode=$code;Log=$log})
    $results|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $run 'results.json') -Encoding utf8
    Get-Content -LiteralPath $log|Write-Host
    if($code -ne 0){throw "Check failed: $Name (exit $code). See $log"}
}
Invoke-Check 'extension-core' 'tests/extension-core-tests.ps1' @('-ScratchRoot',(Join-Path $run 'core'))
Invoke-Check 'build-core' 'tools/build/build-extension-core.ps1' @('-ScratchRoot',(Join-Path $run 'build'),'-OutputRoot',(Join-Path $run 'library'))
if($Mode -eq 'Full'){
    $config=Get-Content -LiteralPath $ConfigPath -Raw|ConvertFrom-Json
    foreach($key in @('GameRoot','LoaderRoot','IcedDll','InterfacesDll')){
        if(-not $config.$key -or -not (Test-Path -LiteralPath $config.$key)){throw "Missing local dependency: $key. Edit $ConfigPath."}
    }
    $exe=Join-Path $config.GameRoot 'FFT_enhanced.exe'
    if(-not(Test-Path -LiteralPath $exe)){throw "Missing game executable: $exe"}
    if((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash -ne '937233F7FE76182A665C487C8802F5CEC6662DDD09967E87CD09FB146FC6B5D5'){throw 'Enhanced executable differs from the audited version; re-audit before native tests.'}
    $samples=Join-Path $run 'samples'
    Invoke-Check 'extract-samples' 'tools/extract/sample-tables.ps1' @('-GameRoot',$config.GameRoot,'-LoaderRoot',$config.LoaderRoot,'-SampleRoot',$samples,'-ReportRoot',(Join-Path $run 'extraction'))
    Invoke-Check 'nxd' 'tests/nxd-tests.ps1' @('-LoaderRoot',$config.LoaderRoot,'-SampleRoot',$samples,'-ScratchRoot',(Join-Path $run 'nxd'))
    Invoke-Check 'additive-nxd' 'tests/additive-nxd-tests.ps1' @('-LoaderRoot',$config.LoaderRoot,'-SampleRoot',$samples,'-ScratchRoot',(Join-Path $run 'additive'))
    Invoke-Check 'native-audit' 'tests/native-audit-tests.ps1' @('-IcedDll',$config.IcedDll,'-AuditPath',(Join-Path $root 'recon-output/native-table-audit.json'))
    Invoke-Check 'consumer-map' 'tests/consumer-map-tests.ps1' @('-IcedDll',$config.IcedDll)
    Invoke-Check 'native-accessors' 'tests/native-accessor-tests.ps1' @('-Executable',$exe,'-ScratchRoot',(Join-Path $run 'native'))
    Invoke-Check 'probe' 'tests/probe-tests.ps1' @('-InterfacesDll',$config.InterfacesDll,'-ScratchRoot',(Join-Path $run 'probe'))
    Invoke-Check 'recon-guards' 'tests/recon-tests.ps1' @('-GameRoot',$config.GameRoot,'-LoaderRoot',$config.LoaderRoot,'-ScratchRoot',(Join-Path $run 'guards'))
}
[pscustomobject]@{Mode=$Mode;CompletedUtc=[DateTime]::UtcNow.ToString('o');Passed=$true;Checks=$results.Count;Results=$results}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $run 'summary.json') -Encoding utf8
Write-Host "PASS $($results.Count) steps. Report: $(Join-Path $run 'summary.json')"
# Full reads game archives and executes copied native routines in its own test process.
# It never starts or patches the game, installs a mod, or reads/writes a real save.
