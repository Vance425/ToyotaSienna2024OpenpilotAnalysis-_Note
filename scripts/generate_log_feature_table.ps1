param(
  [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
  [string[]]$Inputs,
  [string]$OutputDir = "<LOCAL_ANALYSIS_WORKSPACE>\analysis-output",
  [int]$Bus = 0
)

$ErrorActionPreference = "Stop"

$ADDR_116 = 0x116
$ADDR_131 = 0x131
$ADDR_191 = 0x191
$ADDR_260 = 0x260
$ADDR_2E4 = 0x2E4
$ADDR_D8 = 0x0D8

$TOP_TIER_ZONE = "fff4"
$EXIT_ZONE = "fff0"
$CORRIDOR_ZONES = @("fff4", "fff0", "ffee", "ffeb", "ffe8", "ffe7")

function Get-NdjsonFiles {
  param([string[]]$Paths)
  $files = New-Object System.Collections.Generic.List[System.IO.FileInfo]
  foreach ($raw in $Paths) {
    if (Test-Path $raw -PathType Leaf) {
      if ([System.IO.Path]::GetExtension($raw).ToLower() -eq ".ndjson") {
        $files.Add((Get-Item $raw))
      }
      continue
    }
    if (Test-Path $raw -PathType Container) {
      Get-ChildItem $raw -Recurse -Filter *.ndjson -File | ForEach-Object { $files.Add($_) }
    }
  }
  $seen = @{}
  $unique = foreach ($f in $files) {
    if (-not $seen.ContainsKey($f.FullName)) {
      $seen[$f.FullName] = $true
      $f
    }
  }
  return $unique
}

function Get-Hex16 {
  param([int[]]$Data, [int]$Start, [int]$End)
  return (($Data[$Start..($End - 1)] | ForEach-Object { $_.ToString("x2") }) -join "")
}

function Parse-HexBytes {
  param([string]$Hex)
  if ([string]::IsNullOrWhiteSpace($Hex)) {
    throw "empty hex payload"
  }
  if (($Hex.Length % 2) -ne 0) {
    throw "odd-length hex payload"
  }
  $out = New-Object System.Collections.Generic.List[int]
  for ($i = 0; $i -lt $Hex.Length; $i += 2) {
    $out.Add([Convert]::ToInt32($Hex.Substring($i, 2), 16))
  }
  return ,$out.ToArray()
}

function Get-S16LE {
  param([int[]]$Buf, [int]$Idx)
  $v = $Buf[$Idx] -bor ($Buf[$Idx + 1] -shl 8)
  if ($v -band 0x8000) { return $v - 65536 }
  return $v
}

function Get-S16BE {
  param([int[]]$Buf, [int]$Idx)
  $v = ($Buf[$Idx] -shl 8) -bor $Buf[$Idx + 1]
  if ($v -band 0x8000) { return $v - 65536 }
  return $v
}

function Get-S8 {
  param([int]$Value)
  if ($Value -ge 128) { return $Value - 256 }
  return $Value
}

function Get-ControlFrom260 {
  param([int[]]$Buf)
  $fine = Get-S16LE $Buf 2
  $control = $fine + ((Get-S8 $Buf[5]) -shl 8)
  if ($Buf[1] -eq 0xFF) { $control = -$control }
  return $control
}

function Get-Corr {
  param([double[]]$Xs, [double[]]$Ys)
  $n = [Math]::Min($Xs.Count, $Ys.Count)
  if ($n -lt 5) { return $null }
  $mx = (($Xs | Select-Object -First $n | Measure-Object -Sum).Sum) / $n
  $my = (($Ys | Select-Object -First $n | Measure-Object -Sum).Sum) / $n
  $num = 0.0
  $dx = 0.0
  $dy = 0.0
  for ($i = 0; $i -lt $n; $i++) {
    $x = $Xs[$i] - $mx
    $y = $Ys[$i] - $my
    $num += $x * $y
    $dx += $x * $x
    $dy += $y * $y
  }
  if ($dx -eq 0.0 -or $dy -eq 0.0) { return $null }
  return $num / [Math]::Sqrt($dx * $dy)
}

function Get-OrdinalFromRatio {
  param([double]$Ratio)
  if ($Ratio -le 0.0) { return 0 }
  if ($Ratio -lt 0.10) { return 1 }
  if ($Ratio -lt 0.35) { return 2 }
  return 3
}

function Get-JoinedLifecycleStrength {
  param([bool]$HasSeed, [bool]$HasRamp, [bool]$HasPlateau, [bool]$HasExit)
  if ($HasSeed -and $HasRamp -and $HasPlateau -and $HasExit) { return 3 }
  if ($HasSeed -and $HasRamp -and $HasPlateau) { return 2 }
  if ($HasSeed -and $HasRamp) { return 1 }
  return 0
}

function Get-LadderLevel {
  param([string]$Grade, [bool]$HasSeed, [bool]$HasRamp, [bool]$HasPlateau, [bool]$HasExit, [double]$CorridorRatio)
  if ($Grade -eq "A") { return "5" }
  if ($HasSeed -and $HasRamp -and $HasPlateau) { return "4.5_candidate" }
  if ($HasSeed -and $HasRamp) { return "3" }
  if ($HasSeed -and $CorridorRatio -ge 0.20) { return "2" }
  if ($HasSeed) { return "1" }
  if ($CorridorRatio -ge 0.20) { return "C_only" }
  return ""
}

function Get-ValueType {
  param([string]$Grade, [bool]$HasSeed, [bool]$HasRamp, [bool]$HasPlateau, [string]$CompanionMode, $AbsB45, $AbsB67)
  if ($Grade -eq "A") { return "full_event" }
  if ($HasSeed -or $HasRamp -or $HasPlateau) { return "entry_side" }
  $b45 = if ($null -eq $AbsB45 -or $AbsB45 -eq "") { 0.0 } else { [double]$AbsB45 }
  $b67 = if ($null -eq $AbsB67 -or $AbsB67 -eq "") { 0.0 } else { [double]$AbsB67 }
  $best = [Math]::Max($b45, $b67)
  if ($best -ge 0.20 -or @("b4-b5", "b6-b7", "dual") -contains $CompanionMode) {
    return "companion_control"
  }
  return "low_signal"
}

function Analyze-NdjsonFile {
  param([System.IO.FileInfo]$File, [int]$PreferredBus)

  $latest131 = $null
  $latest260 = $null
  $last191 = $null
  $frames116 = New-Object System.Collections.Generic.List[object]
  $controlVals = New-Object System.Collections.Generic.List[double]
  $compB45 = New-Object System.Collections.Generic.List[double]
  $compB67 = New-Object System.Collections.Generic.List[double]

  $count2E4 = 0
  $countD8 = 0
  $totalBusRows = 0
  $parseErrors = 0
  $firstTs = $null
  $lastTs = $null

  Get-Content $File.FullName | ForEach-Object {
    $line = $_.Trim()
    if (-not $line) { return }
    try {
      $row = $line | ConvertFrom-Json
    } catch {
      $parseErrors++
      return
    }
    if ($row.bus -ne $PreferredBus) { return }
    $totalBusRows++
    $addr = [int]$row.addr
    $tsMs = [int64]$row.ts_ms
    $dataHex = [string]$row.data
    if (-not $firstTs) { $firstTs = $tsMs }
    $lastTs = $tsMs

    try {
      $buf = Parse-HexBytes $dataHex
    } catch {
      $parseErrors++
      return
    }

    switch ($addr) {
      $ADDR_131 {
        if ($buf.Length -ge 4) { $latest131 = @($tsMs, (Get-Hex16 $buf 2 4)) }
      }
      $ADDR_260 {
        if ($buf.Length -ge 5) {
          $latest260 = @($tsMs, (Get-Hex16 $buf 3 5))
          if ($null -ne $last191 -and [Math]::Abs($tsMs - $last191[0]) -le 100 -and $buf.Length -ge 8) {
            $controlVals.Add([double](Get-ControlFrom260 $buf))
            $compB45.Add([double]$last191[1])
            $compB67.Add([double]$last191[2])
          }
        }
      }
      $ADDR_116 {
        if ($buf.Length -ge 2) {
          $fam131 = $null
          $fam260 = $null
          if ($null -ne $latest131 -and ($tsMs - $latest131[0]) -le 250) { $fam131 = $latest131[1] }
          if ($null -ne $latest260 -and ($tsMs - $latest260[0]) -le 250) { $fam260 = $latest260[1] }
          $frames116.Add([pscustomobject]@{
              ts_ms     = $tsMs
              phase_sum = [int]$buf[0] + [int]$buf[1]
              phase_hex = (Get-Hex16 $buf 0 2)
              family131 = $fam131
              family260 = $fam260
            })
        }
      }
      $ADDR_191 {
        if ($buf.Length -ge 8) {
          $last191 = @($tsMs, (Get-S16LE $buf 4), (Get-S16BE $buf 6))
        }
      }
      $ADDR_2E4 { $count2E4++ }
      $ADDR_D8 { $countD8++ }
    }
  }

  $hasSeed = $false
  $hasRamp = $false
  $hasPlateau = $false
  $hasExit = $false
  $topTierPeakCount = 0
  $corridorHits = 0
  $alignedHits = 0
  $fff4Hits = 0
  $family131Values = @{}
  $family260Values = @{}

  foreach ($frame in $frames116) {
    $fam131 = $frame.family131
    $fam260 = $frame.family260
    if ($fam131) { $family131Values[$fam131] = 1 + $(if ($family131Values.ContainsKey($fam131)) { $family131Values[$fam131] } else { 0 }) }
    if ($fam260) { $family260Values[$fam260] = 1 + $(if ($family260Values.ContainsKey($fam260)) { $family260Values[$fam260] } else { 0 }) }
    if ($fam131 -and $fam260 -and $fam131 -eq $fam260) { $alignedHits++ }
    if ($CORRIDOR_ZONES -contains $fam131 -and $CORRIDOR_ZONES -contains $fam260) { $corridorHits++ }
    if ($fam131 -eq $TOP_TIER_ZONE -and $fam260 -eq $TOP_TIER_ZONE) {
      $fff4Hits++
      if ($frame.phase_hex -eq "0000") { $hasSeed = $true }
      if ($frame.phase_sum -ge 1 -and $frame.phase_sum -lt 130) { $hasRamp = $true }
      if ($frame.phase_sum -ge 130) {
        $hasPlateau = $true
        $topTierPeakCount++
      }
    }
    if ($hasPlateau -and $fam131 -eq $TOP_TIER_ZONE -and $fam260 -eq $EXIT_ZONE) {
      $hasExit = $true
    }
  }

  $grade = "D"
  if ($hasSeed -and $hasRamp -and $hasPlateau -and $hasExit) {
    $grade = "A"
  } elseif ($hasSeed) {
    $grade = "B"
  } elseif ($corridorHits -gt 0) {
    $grade = "C"
  }

  $c45 = Get-Corr $controlVals.ToArray() $compB45.ToArray()
  $c67 = Get-Corr $controlVals.ToArray() $compB67.ToArray()
  $absB45 = if ($null -eq $c45) { $null } else { [Math]::Abs($c45) }
  $absB67 = if ($null -eq $c67) { $null } else { [Math]::Abs($c67) }

  $companionMode = "insufficient"
  if ($null -ne $c45 -and $null -ne $c67) {
    if ([Math]::Abs($c45) -gt ([Math]::Abs($c67) + 0.05)) {
      $companionMode = "b4-b5"
    } elseif ([Math]::Abs($c67) -gt ([Math]::Abs($c45) + 0.05)) {
      $companionMode = "b6-b7"
    } else {
      $companionMode = "dual"
    }
  }

  $frame116Count = $frames116.Count
  $corridorRatio = if ($frame116Count -eq 0) { 0.0 } else { $corridorHits / $frame116Count }
  $alignedRatio = if ($frame116Count -eq 0) { 0.0 } else { $alignedHits / $frame116Count }
  $fff4Ratio = if ($frame116Count -eq 0) { 0.0 } else { $fff4Hits / $frame116Count }

  $family131Primary = if ($family131Values.Count -eq 0) { "" } else { ($family131Values.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key }
  $family260Primary = if ($family260Values.Count -eq 0) { "" } else { ($family260Values.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key }

  $joinedStrength = Get-JoinedLifecycleStrength $hasSeed $hasRamp $hasPlateau $hasExit
  $ladder = Get-LadderLevel $grade $hasSeed $hasRamp $hasPlateau $hasExit $corridorRatio
  $valueType = Get-ValueType $grade $hasSeed $hasRamp $hasPlateau $companionMode $absB45 $absB67

  return [pscustomobject]@{
    sample_id                           = $File.BaseName
    sample_path                         = $File.FullName
    value_type_primary                  = $valueType
    ladder_level                        = $ladder
    grade                               = $grade
    frame116_count                      = $frame116Count
    duration_min                        = if ($null -eq $firstTs -or $null -eq $lastTs) { "" } else { [Math]::Round(($lastTs - $firstTs) / 60000.0, 2) }
    seed_touch_present                  = [int]$hasSeed
    ramp_present                        = [int]$hasRamp
    phase_plateau_present               = [int]$hasPlateau
    phase_exit_present                  = [int]$hasExit
    joined_lifecycle_strength           = $joinedStrength
    family_131_primary_zone             = $family131Primary
    family_260_primary_zone             = $family260Primary
    family_131_260_aligned              = Get-OrdinalFromRatio $alignedRatio
    family_fff4_presence                = Get-OrdinalFromRatio $fff4Ratio
    corridor_match_strength             = Get-OrdinalFromRatio $corridorRatio
    id_2e4_activity_level               = if ($totalBusRows -eq 0) { 0 } else { Get-OrdinalFromRatio ($count2E4 / $totalBusRows) }
    id_d8_structural_reference_strength = if ($totalBusRows -eq 0) { 0 } else { Get-OrdinalFromRatio ($countD8 / $totalBusRows) }
    companion_primary_mode              = $companionMode
    companion_b45_abs_corr              = if ($null -eq $absB45) { "" } else { [Math]::Round($absB45, 3) }
    companion_b67_abs_corr              = if ($null -eq $absB67) { "" } else { [Math]::Round($absB67, 3) }
    disengage_suspect_present           = ""
    lane_change_transition_present      = ""
    active_core_present                 = ""
    late_stop_present                   = ""
    bridge_candidate                    = if ($ladder -eq "4.5_candidate") { "yes" } else { "no" }
    top_tier_peak_count                 = $topTierPeakCount
    parse_errors                        = $parseErrors
    notes                               = ""
  }
}

$files = Get-NdjsonFiles $Inputs
if (-not $files -or $files.Count -eq 0) {
  throw "No .ndjson files found."
}

$rows = @(foreach ($file in $files) {
  Analyze-NdjsonFile -File $file -PreferredBus $Bus
})

$allCsv = Join-Path $OutputDir "all_ndjson_feature_table.csv"
$allJson = Join-Path $OutputDir "all_ndjson_feature_table.json"
$valuableCsv = Join-Path $OutputDir "valuable_ndjson_feature_table.csv"
$valuableJson = Join-Path $OutputDir "valuable_ndjson_feature_table.json"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$rows | Export-Csv -Path $allCsv -NoTypeInformation -Encoding UTF8
$rows | ConvertTo-Json -Depth 5 | Set-Content -Path $allJson -Encoding UTF8

$valuableRows = @($rows | Where-Object {
  $_.grade -in @("A", "B", "C") -or
  $_.joined_lifecycle_strength -gt 0 -or
  $_.corridor_match_strength -gt 0 -or
  $_.companion_primary_mode -in @("b4-b5", "b6-b7", "dual")
})
$valuableRows | Export-Csv -Path $valuableCsv -NoTypeInformation -Encoding UTF8
$valuableRows | ConvertTo-Json -Depth 5 | Set-Content -Path $valuableJson -Encoding UTF8

Write-Host "all rows: $($rows.Count)"
Write-Host "valuable rows: $($valuableRows.Count)"
Write-Host "all csv: $allCsv"
Write-Host "valuable csv: $valuableCsv"
