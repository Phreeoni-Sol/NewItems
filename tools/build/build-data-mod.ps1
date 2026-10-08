param([string]$PlanPath,[switch]$DryRun)
$ErrorActionPreference='Stop'
throw 'Existing-job replacement is forbidden by the user. Additive runtime registration is not validated yet; no mod files generated. See docs/additive-extension.md.'
