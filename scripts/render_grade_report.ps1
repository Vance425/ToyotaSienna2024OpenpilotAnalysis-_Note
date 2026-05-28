param(
  [string]$InputJson = "<LOCAL_ANALYSIS_WORKSPACE>\analysis-output\can_log_grades.json",
  [string]$OutputPath = "<LOCAL_ANALYSIS_WORKSPACE>\practical\latest-auto-grade-report.md"
)

if (-not (Test-Path $InputJson -PathType Leaf)) {
  throw "Input JSON not found: $InputJson"
}

$rows = Get-Content -Path $InputJson -Raw | ConvertFrom-Json
if (-not $rows) {
  throw "No rows found in $InputJson"
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
$gradeCounts = @{
  A = @($rows | Where-Object grade -eq "A").Count
  B = @($rows | Where-Object grade -eq "B").Count
  C = @($rows | Where-Object grade -eq "C").Count
  D = @($rows | Where-Object grade -eq "D").Count
}

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Auto Grade Report")
$lines.Add("")
$lines.Add(("Generated: {0}" -f $timestamp))
$lines.Add("")
$lines.Add("## Summary")
$lines.Add("")
$lines.Add(("- ``Grade A``: {0}" -f $gradeCounts.A))
$lines.Add(("- ``Grade B``: {0}" -f $gradeCounts.B))
$lines.Add(("- ``Grade C``: {0}" -f $gradeCounts.C))
$lines.Add(("- ``Grade D``: {0}" -f $gradeCounts.D))
$lines.Add("")
$lines.Add("## Matrix")
$lines.Add("")
$lines.Add("| file | grade | seed | ramp | plateau | exit | corridor | note |")
$lines.Add("| --- | --- | --- | --- | --- | --- | --- | --- |")

foreach ($row in $rows) {
  $name = Split-Path -Leaf $row.file
  $pathForMd = $row.file.Replace('\','/')
  $lines.Add(("| [{0}]({1}) | ``{2}`` | ``{3}`` | ``{4}`` | ``{5}`` | ``{6}`` | ``{7}`` | {8} |" -f $name, $pathForMd, $row.grade, $row.has_seed, $row.has_ramp, $row.has_plateau, $row.has_exit, $row.has_corridor, $row.reason))
}

$lines.Add("")
$lines.Add("## Review Queue")
$lines.Add("")

$gradeA = @($rows | Where-Object grade -eq "A")
$gradeB = @($rows | Where-Object grade -eq "B")

if ($gradeA.Count -gt 0) {
  $lines.Add("### Grade A")
  $lines.Add("")
  foreach ($row in $gradeA) {
    $name = Split-Path -Leaf $row.file
    $pathForMd = $row.file.Replace('\','/')
    $lines.Add(("- [{0}]({1})" -f $name, $pathForMd))
    $lines.Add(("  seed=``{0}`` plateau=``{1}`` peaks=``{2}``" -f $row.seed_ts, $row.plateau_ts, $row.top_tier_peak_count))
  }
  $lines.Add("")
}

if ($gradeB.Count -gt 0) {
  $lines.Add("### Grade B")
  $lines.Add("")
  foreach ($row in $gradeB) {
    $name = Split-Path -Leaf $row.file
    $pathForMd = $row.file.Replace('\','/')
    $lines.Add(("- [{0}]({1})" -f $name, $pathForMd))
    $lines.Add(("  seed=``{0}`` ramp=``{1}`` corridor=``{2}``" -f $row.seed_ts, $row.has_ramp, $row.has_corridor))
    if ($row.positive_high_phase_examples -and $row.positive_high_phase_examples.Count -gt 0) {
      $sample = $row.positive_high_phase_examples[0]
      $lines.Add(("  high-phase-counterexample=``{0}`` family131=``{1}`` family260=``{2}`` ts=``{3}``" -f $sample.phase_hex, $sample.family131, $sample.family260, $sample.ts_ms))
    }
  }
  $lines.Add("")
}

$lines.Add("## Notes")
$lines.Add("")
$lines.Add("- `Grade A` should be reviewed against the top-tier lifecycle template.")
$lines.Add("- ``Grade B`` should be checked for whether it only touches ``fff4|fff4 + 00 00``.")
$lines.Add("- High phase in positive family zones is not sufficient for top-tier classification.")

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPath) | Out-Null
Set-Content -Path $OutputPath -Value $lines -Encoding utf8

Write-Output "Report: $OutputPath"
