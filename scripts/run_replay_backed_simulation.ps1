param(
  [string]$PythonCmd = "python",
  [string]$OutputDir = "<LOCAL_ANALYSIS_WORKSPACE>\analysis-output\replay_simulation",
  [double[]]$Slew = @(10, 25, 50, 75, 100),
  [switch]$EmitOnly
)

$ScriptPath = "<LOCAL_ANALYSIS_WORKSPACE>\scripts\replay_backed_simulation.py"

$cmdArgs = @(
  $ScriptPath,
  "--output-dir", $OutputDir
)

foreach ($limit in $Slew) {
  $cmdArgs += @("--slew", "$limit")
}

if ($EmitOnly) {
  Write-Host ($PythonCmd + " " + ($cmdArgs -join " "))
  exit 0
}

Write-Host "Running replay-backed simulation harness"
& $PythonCmd @cmdArgs
if ($LASTEXITCODE -ne 0) {
  throw "Replay-backed simulation harness failed"
}
