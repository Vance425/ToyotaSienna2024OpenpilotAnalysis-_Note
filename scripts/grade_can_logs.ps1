param(
  [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
  [string[]]$Inputs,
  [string]$OutputDir = "<LOCAL_ANALYSIS_WORKSPACE>\analysis-output",
  [int]$Bus = 0
)

$Addr116 = 0x116
$Addr131 = 0x131
$Addr260 = 0x260
$TopTierZone = "fff4"
$ExitZone = "fff0"
$CorridorZones = @("fff4", "fff0", "ffee", "ffeb", "ffe8", "ffe7")

function Get-NdjsonFiles {
  param([string[]]$Sources)
  $files = New-Object System.Collections.Generic.List[string]
  foreach ($src in $Sources) {
    if (Test-Path $src -PathType Leaf) {
      if ([System.IO.Path]::GetExtension($src).ToLowerInvariant() -eq ".ndjson") {
        $files.Add((Resolve-Path $src).Path)
      }
      continue
    }
    if (Test-Path $src -PathType Container) {
      Get-ChildItem -Path $src -Recurse -Filter *.ndjson -File | ForEach-Object {
        $files.Add($_.FullName)
      }
    }
  }
  return $files | Sort-Object -Unique
}

function Get-HexSlice {
  param(
    [byte[]]$Bytes,
    [int]$Start,
    [int]$Count
  )
  return -join ($Bytes[$Start..($Start + $Count - 1)] | ForEach-Object { $_.ToString("x2") })
}

function Analyze-Log {
  param(
    [string]$Path,
    [int]$PreferredBus
  )

  $latest131 = $null
  $latest260 = $null
  $frames116 = New-Object System.Collections.Generic.List[object]
  $busCounts = @{}
  $parseErrors = 0

  Get-Content -Path $Path | ForEach-Object {
    if ([string]::IsNullOrWhiteSpace($_)) {
      return
    }

    if ($_ -notlike "*""bus"":$PreferredBus*") {
      return
    }
    if ($_ -notlike "*""addr"":$Addr116*" -and $_ -notlike "*""addr"":$Addr131*" -and $_ -notlike "*""addr"":$Addr260*") {
      return
    }

    try {
      $row = $_ | ConvertFrom-Json
    } catch {
      $parseErrors += 1
      return
    }

    $bus = [int]$row.bus
    $addr = [int]$row.addr
    $tsMs = [int64]$row.ts_ms
    $dataHex = [string]$row.data

    if (-not $busCounts.ContainsKey($bus)) {
      $busCounts[$bus] = 0
    }
    $busCounts[$bus] += 1

    try {
      $bytes = for ($i = 0; $i -lt $dataHex.Length; $i += 2) {
        [Convert]::ToByte($dataHex.Substring($i, 2), 16)
      }
    } catch {
      $parseErrors += 1
      return
    }

    if ($addr -eq $Addr131 -and $bytes.Length -ge 4) {
      $latest131 = @{
        ts_ms = $tsMs
        family = Get-HexSlice -Bytes $bytes -Start 2 -Count 2
      }
      return
    }

    if ($addr -eq $Addr260 -and $bytes.Length -ge 5) {
      $latest260 = @{
        ts_ms = $tsMs
        family = Get-HexSlice -Bytes $bytes -Start 3 -Count 2
      }
      return
    }

    if ($addr -eq $Addr116 -and $bytes.Length -ge 2) {
      $family131 = $null
      $family260 = $null
      if ($latest131 -and (($tsMs - $latest131.ts_ms) -le 250)) {
        $family131 = $latest131.family
      }
      if ($latest260 -and (($tsMs - $latest260.ts_ms) -le 250)) {
        $family260 = $latest260.family
      }

      $frames116.Add([pscustomobject]@{
        ts_ms = $tsMs
        phase_hex = Get-HexSlice -Bytes $bytes -Start 0 -Count 2
        phase_sum = ([int]$bytes[0] + [int]$bytes[1])
        family131 = $family131
        family260 = $family260
        raw_data = $dataHex
      })
    }
  }

  $hasSeed = $false
  $hasRamp = $false
  $hasPlateau = $false
  $hasExit = $false
  $hasCorridor = $false
  $seedTs = $null
  $plateauTs = $null
  $topTierPeaks = New-Object System.Collections.Generic.List[object]
  $positiveHighPhasePeaks = New-Object System.Collections.Generic.List[object]

  foreach ($frame in $frames116) {
    if ($CorridorZones -contains $frame.family131 -and $CorridorZones -contains $frame.family260) {
      $hasCorridor = $true
    }

    if ($frame.family131 -eq $TopTierZone -and $frame.family260 -eq $TopTierZone) {
      if ($frame.phase_hex -eq "0000") {
        $hasSeed = $true
        if (-not $seedTs) {
          $seedTs = $frame.ts_ms
        }
      }
      if ($frame.phase_sum -ge 130) {
        $hasPlateau = $true
        if (-not $plateauTs) {
          $plateauTs = $frame.ts_ms
        }
        if ($topTierPeaks.Count -lt 5) {
          $topTierPeaks.Add($frame)
        }
      }
      if ($frame.phase_sum -ge 1 -and $frame.phase_sum -lt 130) {
        $hasRamp = $true
      }
    } elseif ($frame.phase_sum -ge 130 -and (-not ($CorridorZones -contains $frame.family131 -and $CorridorZones -contains $frame.family260))) {
      if ($positiveHighPhasePeaks.Count -lt 5) {
        $positiveHighPhasePeaks.Add($frame)
      }
    }

    if ($plateauTs -and $frame.ts_ms -ge $plateauTs -and $frame.family131 -eq $TopTierZone -and $frame.family260 -eq $ExitZone) {
      $hasExit = $true
    }
  }

  $grade = "D"
  $reason = "no seed/corridor pattern"
  if ($hasSeed -and $hasRamp -and $hasPlateau -and $hasExit) {
    $grade = "A"
    $reason = "seed + ramp + plateau + exit under fff4/fff0 pattern"
  } elseif ($hasSeed) {
    $grade = "B"
    $reason = "touches fff4|fff4 + 0000 but lacks full lifecycle"
  } elseif ($hasCorridor) {
    $grade = "C"
    $reason = "corridor activity without full seed state"
  }

  return [pscustomobject]@{
    file = $Path
    bus = $PreferredBus
    parse_errors = $parseErrors
    bus_counts = $busCounts
    frame116_count = $frames116.Count
    grade = $grade
    reason = $reason
    has_seed = $hasSeed
    has_ramp = $hasRamp
    has_plateau = $hasPlateau
    has_exit = $hasExit
    has_corridor = $hasCorridor
    seed_ts = $seedTs
    plateau_ts = $plateauTs
    top_tier_peak_count = $topTierPeaks.Count
    top_tier_peak_examples = $topTierPeaks
    positive_high_phase_examples = $positiveHighPhasePeaks
  }
}

$files = Get-NdjsonFiles -Sources $Inputs
if (-not $files -or $files.Count -eq 0) {
  throw "No .ndjson files found."
}

$results = foreach ($file in $files) {
  Analyze-Log -Path $file -PreferredBus $Bus
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$csvPath = Join-Path $OutputDir "can_log_grades.csv"
$jsonPath = Join-Path $OutputDir "can_log_grades.json"

$results |
  Select-Object file, grade, reason, has_seed, has_ramp, has_plateau, has_exit, has_corridor, seed_ts, plateau_ts, top_tier_peak_count, frame116_count |
  Export-Csv -Path $csvPath -NoTypeInformation -Encoding utf8

$jsonReady = foreach ($row in $results) {
  [pscustomobject]@{
    file = $row.file
    bus = $row.bus
    parse_errors = $row.parse_errors
    bus_counts = @($row.bus_counts.GetEnumerator() | ForEach-Object {
      [pscustomobject]@{
        bus = [string]$_.Key
        count = $_.Value
      }
    })
    frame116_count = $row.frame116_count
    grade = $row.grade
    reason = $row.reason
    has_seed = $row.has_seed
    has_ramp = $row.has_ramp
    has_plateau = $row.has_plateau
    has_exit = $row.has_exit
    has_corridor = $row.has_corridor
    seed_ts = $row.seed_ts
    plateau_ts = $row.plateau_ts
    top_tier_peak_count = $row.top_tier_peak_count
    top_tier_peak_examples = $row.top_tier_peak_examples
    positive_high_phase_examples = $row.positive_high_phase_examples
  }
}

$jsonReady | ConvertTo-Json -Depth 6 | Set-Content -Path $jsonPath -Encoding utf8

foreach ($row in $results) {
  Write-Output ("{0}  {1}  {2}" -f $row.grade, $row.file, $row.reason)
}
Write-Output ""
Write-Output ("CSV:  {0}" -f $csvPath)
Write-Output ("JSON: {0}" -f $jsonPath)
