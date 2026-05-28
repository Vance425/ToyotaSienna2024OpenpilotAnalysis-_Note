param(
  [string]$RepoRoot = "<LOCAL_ANALYSIS_WORKSPACE>",
  [string]$OutDir = "<LOCAL_ANALYSIS_WORKSPACE>\share_bundle"
)

$ErrorActionPreference = "Stop"

$practicalDir = Join-Path $RepoRoot "practical"
$scriptsDir = Join-Path $RepoRoot "scripts"
$simDir = Join-Path $RepoRoot "sim"
$outDocs = Join-Path $OutDir "docs"
$outScripts = Join-Path $OutDir "scripts"
$outLogs = Join-Path $OutDir "logs"
$outSim = Join-Path $OutDir "sim"

$shareLogs = @(
  @{
    Source = "<LOCAL_RAW_CAN_LOG>\toyota_seg_IGN_ON_20260312_190101_000.ndjson"
    Target = "toyota_seg_IGN_ON_20260312_190101_000.ndjson"
    Role = "Top-tier joined lifecycle anchor"
  },
  @{
    Source = "<LOCAL_RAW_CAN_LOG>\20260316\raw_can_logs\toyota_seg_IGN_ON_20260315_171414_000.ndjson"
    Target = "toyota_seg_IGN_ON_20260315_171414_000.ndjson"
    Role = "Strongest older partial-ramp / seed-heavy entry-side sample"
  },
  @{
    Source = "<LOCAL_RAW_CAN_LOG>\toyota_seg_IGN_ON_20260312_185520_000.ndjson"
    Target = "toyota_seg_IGN_ON_20260312_185520_000.ndjson"
    Role = "Compact early partial-seed / seed-touch-only sample"
  },
  @{
    Source = "<LOCAL_RAW_CAN_LOG>\20260314\raw_can_logs\toyota_seg_IGN_ON_20260314_173834_000.ndjson"
    Target = "toyota_seg_IGN_ON_20260314_173834_000.ndjson"
    Role = "Ramping bridge sample"
  },
  @{
    Source = "<LOCAL_RAW_CAN_LOG>\toyota_seg_IGN_ON_20260311_184921_000.ndjson"
    Target = "toyota_seg_IGN_ON_20260311_184921_000.ndjson"
    Role = "Compact ramping partial sample"
  },
  @{
    Source = "<LOCAL_RAW_CAN_LOG>\20260316\raw_can_logs\toyota_seg_IGN_ON_20260315_175912_004.ndjson"
    Target = "toyota_seg_IGN_ON_20260315_175912_004.ndjson"
    Role = "Plateau-heavy highway-side mixed companion reference"
  },
  @{
    Source = "<LOCAL_RAW_CAN_LOG>\20260314\raw_can_logs\toyota_seg_IGN_ON_20260314_175006_001.ndjson"
    Target = "toyota_seg_IGN_ON_20260314_175006_001.ndjson"
    Role = "Freeway-like mixed sample / primary lane-change-transition reference"
  },
  @{
    Source = "<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_all_20260418_163135_000.ndjson"
    Target = "toyota_all_20260418_163135_000.ndjson"
    Role = "City session reference containing active-core urban windows"
  },
  @{
    Source = "<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_all_20260418_175240_000.ndjson"
    Target = "toyota_all_20260418_175240_000.ndjson"
    Role = "City session reference containing hold / late-stop windows"
  }
)

if (Test-Path $OutDir) {
  Remove-Item -Recurse -Force $OutDir
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
New-Item -ItemType Directory -Force -Path $outDocs | Out-Null
New-Item -ItemType Directory -Force -Path $outScripts | Out-Null
New-Item -ItemType Directory -Force -Path $outLogs | Out-Null
New-Item -ItemType Directory -Force -Path $outSim | Out-Null

$docFiles = Get-ChildItem -Path $practicalDir -Filter *.md -File
$scriptFiles = Get-ChildItem -Path $scriptsDir -File
$simFiles = @()
if (Test-Path $simDir) {
  $simFiles = Get-ChildItem -Path $simDir -File
}

foreach ($file in $scriptFiles) {
  Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $outScripts $file.Name)
}

foreach ($file in $simFiles) {
  Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $outSim $file.Name)
}

foreach ($entry in $shareLogs) {
  if (Test-Path $entry.Source) {
    Copy-Item -LiteralPath $entry.Source -Destination (Join-Path $outLogs $entry.Target)
  }
}

function Convert-MarkdownContent {
  param(
    [string]$Text
  )

  $converted = $Text

  # practical docs -> local docs bundle
  $converted = [regex]::Replace(
    $converted,
    '\[([^\]]+)\]\(/D:/Codex/toyota-sienna-tsk-analysis/practical/([^)]+)\)',
    {
      param($m)
      $label = $m.Groups[1].Value
      $name = [System.IO.Path]::GetFileName($m.Groups[2].Value)
      return "[$label](./$name)"
    }
  )

  # script links -> bundled scripts
  $converted = [regex]::Replace(
    $converted,
    '\[([^\]]+)\]\(/D:/Codex/toyota-sienna-tsk-analysis/scripts/([^)]+)\)',
    {
      param($m)
      $label = $m.Groups[1].Value
      $name = [System.IO.Path]::GetFileName($m.Groups[2].Value)
      return "[$label](../scripts/$name)"
    }
  )

  # root-level project notes -> bundle root
  $converted = [regex]::Replace(
    $converted,
    '\[([^\]]+)\]\(/D:/Codex/toyota-sienna-tsk-analysis/([^/)]+\.md)\)',
    {
      param($m)
      $label = $m.Groups[1].Value
      $name = [System.IO.Path]::GetFileName($m.Groups[2].Value)
      return "[$label](../$name)"
    }
  )

  # temp/raw log links -> local-only placeholder
  $converted = [regex]::Replace(
    $converted,
    '\[([^\]]+)\]\(/D:/Temp/([^)]+)\)',
    {
      param($m)
      $label = $m.Groups[1].Value
      $matchedPath = '<LOCAL_TEMP>\' + ($m.Groups[2].Value -replace '/', '\')
      $hit = $shareLogs | Where-Object { $_.Source -eq $matchedPath } | Select-Object -First 1
      if ($null -ne $hit) {
        return "[$label](../logs/$($hit.Target))"
      }
      return "`$label` (local-only source path)"
    }
  )

  return $converted
}

foreach ($file in $docFiles) {
  $text = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
  $converted = Convert-MarkdownContent -Text $text
  Set-Content -LiteralPath (Join-Path $outDocs $file.Name) -Value ($converted.TrimEnd() + [Environment]::NewLine) -Encoding UTF8 -NoNewline
}

$includedLogs = @(
  "# Included Representative Logs",
  "",
  "This share bundle includes a curated subset of raw logs that represent the current research model.",
  "",
  "## Included Files",
  ""
)

foreach ($entry in $shareLogs) {
  if (Test-Path (Join-Path $outLogs $entry.Target)) {
    $includedLogs += "- [$($entry.Target)](../logs/$($entry.Target))"
    $includedLogs += "  - role: $($entry.Role)"
  }
}

Set-Content -LiteralPath (Join-Path $outDocs "included-logs.md") -Value ($includedLogs -join [Environment]::NewLine) -Encoding UTF8

$readmeLines = @(
  '# Toyota Sienna TSK Research Share Bundle',
  '',
  'This bundle is a collaborator-friendly export of the current `Toyota Sienna + comma 3X` `TSK / SecOC` research workspace.',
  '',
  'It includes:',
  '',
  '- the current research summaries',
  '- the most important interpretation memos',
  '- the analysis scripts used in the project',
  '- a curated subset of representative raw CAN logs',
  '',
  '## What This Is',
  '',
  'This package is centered on two parallel lines of work:',
  '',
  '1. **Passive `TSK-nearest` modeling**',
  '   - identify sessions and windows that are closest to protected, key-bound lifecycle behavior',
  '2. **Control / companion interpretation**',
  '   - explain `0x260 / 0x191` regime behavior in city, freeway, and mixed samples',
  '',
  'The current project does **not** claim to directly derive `TSK` from logs alone.',
  '',
  'Instead, the passive work narrows:',
  '',
  '- which logs are closest to `TSK-nearest`',
  '- which windows are strongest',
  '- and where a future direct validation path would be best targeted',
  '',
  '## Start Here',
  '',
  '- [Project Status](./PROJECT_STATUS.md)',
  '- [Current Findings Summary](./docs/current-findings-summary-v2.md)',
  '- [Current Project Status (ZH)](./docs/current-project-status-zh.md)',
  '- [Final Frame Role Map](./docs/final-frame-role-map.md)',
  '- [Virtual TSK Working Spec v2](./docs/VIRTUAL_TSK_SPEC_v2.md)',
  '- [Partner Reading Order (ZH)](./docs/partner-reading-order-zh.md)',
  '- [Passive TSK-Nearest Overview (ZH)](./docs/passive-tsk-nearest-overview-zh.md)',
  '- [TSK-Nearest Ladder](./docs/tsk-nearest-ladder-entry-to-anchor.md)',
  '- [Bridge-Gap Capture Checklist (ZH)](./docs/bridge-gap-capture-checklist-20s-zh.md)',
  '- [Simulation Validation Report](./sim/simulation_report.md)',
  '- [Next-Log Analysis Template](./docs/next-log-analysis-template.md)',
  '- [Public References Map](./docs/public-references-map.md)',
  '- [Public References Map (ZH)](./docs/public-references-map-zh.md)',
  '- [Included Representative Logs](./docs/included-logs.md)',
  '',
  '## Suggested Reading Order',
  '',
  'If you are new to this project, read in this order:',
  '',
  '1. [Partner Reading Order (ZH)](./docs/partner-reading-order-zh.md)',
  '2. [Current Findings Summary](./docs/current-findings-summary-v2.md)',
  '3. [Final Frame Role Map](./docs/final-frame-role-map.md)',
  '4. [TSK-Nearest Ladder](./docs/tsk-nearest-ladder-entry-to-anchor.md)',
  '5. [Passive TSK-Nearest Overview (ZH)](./docs/passive-tsk-nearest-overview-zh.md)',
  '',
  '## Included Representative Logs',
  '',
  'Representative logs are included under:',
  '',
  '- `./logs`',
  '',
  'These are not the full raw-log archive.',
  '',
  'They are a curated set chosen to represent:',
  '',
  '- top-tier joined lifecycle anchor',
  '- partial-ramp / bridge-side samples',
  '- freeway / mixed companion behavior',
  '- city active-core / hold / late-stop references',
  '',
  '## Notes',
  '',
  '- A curated set of representative raw logs is included under `./logs`.',
  '- Other local-only raw log links remain labeled as `local-only source path`.',
  '- Project scripts are included under `./scripts`.',
  '- Simulation artifacts are included under `./sim`.',
  '- This bundle was generated from the local research repo.',
  '',
  '## Current Bottom Line',
  '',
  'The current best passive interpretation is:',
  '',
  '- `0x116 + 0x131/0x116 lifecycle + 0x2E4`',
  '  = main `TSK-nearest` path',
  '- `0x260 / 0x191`',
  '  = control / companion line, useful but not the shortest direct path to `TSK`',
  '',
  'The strongest passive anchor remains:',
  '',
  '- `20260312_190101_000`',
  '',
  'The biggest current passive gap remains:',
  '',
  '- a convincing bridge state between:',
  '  - `171414_000`',
  '  - and',
  '  - `190101_000`'
)

Set-Content -LiteralPath (Join-Path $OutDir "README.md") -Value ($readmeLines -join [Environment]::NewLine) -Encoding UTF8

$gitignoreLines = @(
  '.DS_Store',
  'Thumbs.db',
  'desktop.ini'
)

Set-Content -LiteralPath (Join-Path $OutDir ".gitignore") -Value ($gitignoreLines -join [Environment]::NewLine) -Encoding UTF8

Write-Host "[INFO] share bundle exported to: $OutDir"
Write-Host "[INFO] docs copied:" $docFiles.Count
Write-Host "[INFO] scripts copied:" $scriptFiles.Count
Write-Host "[INFO] logs copied:" ((Get-ChildItem -Path $outLogs -File | Measure-Object).Count)
Write-Host "[INFO] sim files copied:" ((Get-ChildItem -Path $outSim -File | Measure-Object).Count)
