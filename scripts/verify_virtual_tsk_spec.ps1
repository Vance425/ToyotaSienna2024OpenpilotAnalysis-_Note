param(
  [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
  [string[]]$Inputs,
  [string]$OutputDir = "<LOCAL_ANALYSIS_WORKSPACE>\analysis-output\virtual_tsk_verify",
  [int]$Bus = 0
)

$ErrorActionPreference = "Stop"

function Parse-HexBytes {
  param([string]$Hex)
  if ([string]::IsNullOrWhiteSpace($Hex)) { throw "empty hex payload" }
  if (($Hex.Length % 2) -ne 0) { throw "odd-length hex payload" }
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

function Find-LatestIndexAtOrBefore {
  param([object[]]$Series, [int64]$Ts, [int]$StartIndex)
  $idx = $StartIndex
  while (($idx + 1) -lt $Series.Count -and $Series[$idx + 1].ts_ms -le $Ts) {
    $idx++
  }
  return $idx
}

function Find-NextIndexAtOrAfter {
  param([object[]]$Series, [int64]$Ts, [int]$StartIndex)
  $idx = $StartIndex
  while ($idx -lt $Series.Count -and $Series[$idx].ts_ms -lt $Ts) {
    $idx++
  }
  return $idx
}

function Analyze-File {
  param([System.IO.FileInfo]$File, [int]$PreferredBus)

  $series260 = New-Object System.Collections.Generic.List[object]
  $seriesAA = New-Object System.Collections.Generic.List[object]
  $series90 = New-Object System.Collections.Generic.List[object]
  $series127 = New-Object System.Collections.Generic.List[object]
  $series371 = New-Object System.Collections.Generic.List[object]
  $series191 = New-Object System.Collections.Generic.List[object]
  $counts = @{}
  $parseErrors = 0

  Get-Content $File.FullName | ForEach-Object {
    $line = $_.Trim()
    if (-not $line) { return }
    try { $o = $line | ConvertFrom-Json } catch { $parseErrors++; return }
    if ([int]$o.bus -ne $PreferredBus) { return }
    $addr = [int]$o.addr
    $ts = [int64]$o.ts_ms
    $dataHex = [string]$o.data
    $k = ('0x{0:X}' -f $addr)
    if (-not $counts.ContainsKey($k)) { $counts[$k] = 0 }
    $counts[$k]++
    try { $buf = Parse-HexBytes $dataHex } catch { $parseErrors++; return }

    switch ($addr) {
      0x260 {
        if ($buf.Length -ge 8) {
          $series260.Add([pscustomobject]@{
              ts_ms    = $ts
              control  = [double](Get-ControlFrom260 $buf)
              b1       = $buf[1]
              b5_s8    = Get-S8 $buf[5]
            })
        }
      }
      0xAA {
        if ($buf.Length -ge 1) {
          $seriesAA.Add([pscustomobject]@{
              ts_ms = $ts
              b0    = $buf[0]
            })
        }
      }
      0x90 {
        if ($buf.Length -ge 2) {
          $series90.Add([pscustomobject]@{
              ts_ms = $ts
              b0b1  = Get-S16BE $buf 0
            })
        }
      }
      0x127 {
        if ($buf.Length -ge 2) {
          $series127.Add([pscustomobject]@{
              ts_ms = $ts
              b0b1  = Get-S16BE $buf 0
            })
        }
      }
      0x371 {
        if ($buf.Length -ge 4) {
          $series371.Add([pscustomobject]@{
              ts_ms = $ts
              b23_be = [double](Get-S16BE $buf 2)
              b23_le = [double](Get-S16LE $buf 2)
            })
        }
      }
      0x191 {
        if ($buf.Length -ge 8) {
          $series191.Add([pscustomobject]@{
              ts_ms = $ts
              b45   = [double](Get-S16LE $buf 4)
              b67   = [double](Get-S16BE $buf 6)
            })
        }
      }
    }
  }

  $large260 = 0
  for ($i = 1; $i -lt $series260.Count; $i++) {
    if ([Math]::Abs($series260[$i].control - $series260[$i - 1].control) -gt 500) {
      $large260++
      Add-Member -InputObject $series260[$i] -NotePropertyName is_large_change -NotePropertyValue $true -Force
    } else {
      Add-Member -InputObject $series260[$i] -NotePropertyName is_large_change -NotePropertyValue $false -Force
    }
  }
  if ($series260.Count -gt 0) {
    Add-Member -InputObject $series260[0] -NotePropertyName is_large_change -NotePropertyValue $false -Force
  }

  $aaTransitions = New-Object System.Collections.Generic.List[object]
  for ($i = 1; $i -lt $seriesAA.Count; $i++) {
    if ($seriesAA[$i].b0 -ne $seriesAA[$i - 1].b0) {
      $aaTransitions.Add($seriesAA[$i])
    }
  }

  $aaNear = 0
  $aaLargeNear = 0
  $n90Near = 0
  $n127Next = 0
  $n127Changed = 0
  $fb371Near = 0
  $iAA = 0
  $iAAChange = 0
  $i90 = 0
  $i127 = 0
  $i371 = 0
  $x371be = New-Object System.Collections.Generic.List[double]
  $y371be = New-Object System.Collections.Generic.List[double]
  $x371le = New-Object System.Collections.Generic.List[double]
  $y371le = New-Object System.Collections.Generic.List[double]
  $x191b45 = New-Object System.Collections.Generic.List[double]
  $y191b45 = New-Object System.Collections.Generic.List[double]
  $x191b67 = New-Object System.Collections.Generic.List[double]
  $y191b67 = New-Object System.Collections.Generic.List[double]
  $i191 = 0

  foreach ($row in $series260) {
    $ts = $row.ts_ms
    if ($seriesAA.Count -gt 0) {
      $iAA = Find-LatestIndexAtOrBefore $seriesAA.ToArray() $ts $iAA
      if ($iAA -ge 0 -and $iAA -lt $seriesAA.Count -and ($ts - $seriesAA[$iAA].ts_ms) -le 20) { $aaNear++ }
    }
    if ($aaTransitions.Count -gt 0) {
      $iAAChange = Find-LatestIndexAtOrBefore $aaTransitions.ToArray() $ts $iAAChange
      if ($row.is_large_change -and $iAAChange -ge 0 -and $iAAChange -lt $aaTransitions.Count -and ($ts - $aaTransitions[$iAAChange].ts_ms) -le 20) { $aaLargeNear++ }
    }
    if ($series90.Count -gt 0) {
      $i90 = Find-LatestIndexAtOrBefore $series90.ToArray() $ts $i90
      if ($i90 -ge 0 -and $i90 -lt $series90.Count -and ($ts - $series90[$i90].ts_ms) -le 20) { $n90Near++ }
    }
    if ($series127.Count -gt 0) {
      $next127 = Find-NextIndexAtOrAfter $series127.ToArray() $ts $i127
      if ($next127 -lt $series127.Count -and ($series127[$next127].ts_ms - $ts) -le 20) {
        $n127Next++
        if ($next127 -gt 0 -and $series127[$next127].b0b1 -ne $series127[$next127 - 1].b0b1) { $n127Changed++ }
        $i127 = $next127
      }
    }
    if ($series371.Count -gt 0) {
      $next371 = Find-NextIndexAtOrAfter $series371.ToArray() $ts $i371
      if ($next371 -lt $series371.Count -and ($series371[$next371].ts_ms - $ts) -le 50) {
        $fb371Near++
        $x371be.Add($row.control); $y371be.Add($series371[$next371].b23_be)
        $x371le.Add($row.control); $y371le.Add($series371[$next371].b23_le)
        $i371 = $next371
      }
    }
    if ($series191.Count -gt 0) {
      $i191 = Find-LatestIndexAtOrBefore $series191.ToArray() $ts $i191
      if ($i191 -ge 0 -and $i191 -lt $series191.Count -and [Math]::Abs($ts - $series191[$i191].ts_ms) -le 100) {
        $x191b45.Add($row.control); $y191b45.Add($series191[$i191].b45)
        $x191b67.Add($row.control); $y191b67.Add($series191[$i191].b67)
      }
    }
  }

  $corr371be = Get-Corr $x371be.ToArray() $y371be.ToArray()
  $corr371le = Get-Corr $x371le.ToArray() $y371le.ToArray()
  $corr191b45 = Get-Corr $x191b45.ToArray() $y191b45.ToArray()
  $corr191b67 = Get-Corr $x191b67.ToArray() $y191b67.ToArray()

  return [pscustomobject]@{
    sample_id = $File.BaseName
    sample_path = $File.FullName
    parse_errors = $parseErrors
    count_260 = if ($counts.ContainsKey('0x260')) { $counts['0x260'] } else { 0 }
    count_AA = if ($counts.ContainsKey('0xAA')) { $counts['0xAA'] } else { 0 }
    count_90 = if ($counts.ContainsKey('0x90')) { $counts['0x90'] } else { 0 }
    count_127 = if ($counts.ContainsKey('0x127')) { $counts['0x127'] } else { 0 }
    count_371 = if ($counts.ContainsKey('0x371')) { $counts['0x371'] } else { 0 }
    count_101 = if ($counts.ContainsKey('0x101')) { $counts['0x101'] } else { 0 }
    count_108 = if ($counts.ContainsKey('0x108')) { $counts['0x108'] } else { 0 }
    count_116 = if ($counts.ContainsKey('0x116')) { $counts['0x116'] } else { 0 }
    count_131 = if ($counts.ContainsKey('0x131')) { $counts['0x131'] } else { 0 }
    count_2E4 = if ($counts.ContainsKey('0x2E4')) { $counts['0x2E4'] } else { 0 }
    aa_near_260_ratio = if ($series260.Count -eq 0) { $null } else { [Math]::Round($aaNear / $series260.Count, 3) }
    aa_transition_near_large260_ratio = if ($large260 -eq 0) { $null } else { [Math]::Round($aaLargeNear / $large260, 3) }
    n90_near_260_ratio = if ($series260.Count -eq 0) { $null } else { [Math]::Round($n90Near / $series260.Count, 3) }
    n127_after_260_ratio = if ($series260.Count -eq 0) { $null } else { [Math]::Round($n127Next / $series260.Count, 3) }
    n127_changed_after_260_ratio = if ($n127Next -eq 0) { $null } else { [Math]::Round($n127Changed / $n127Next, 3) }
    n371_after_260_ratio = if ($series260.Count -eq 0) { $null } else { [Math]::Round($fb371Near / $series260.Count, 3) }
    corr_260_to_371_b23_be = if ($null -eq $corr371be) { $null } else { [Math]::Round($corr371be, 3) }
    corr_260_to_371_b23_le = if ($null -eq $corr371le) { $null } else { [Math]::Round($corr371le, 3) }
    corr_260_to_191_b45 = if ($null -eq $corr191b45) { $null } else { [Math]::Round($corr191b45, 3) }
    corr_260_to_191_b67 = if ($null -eq $corr191b67) { $null } else { [Math]::Round($corr191b67, 3) }
  }
}

$files = Get-NdjsonFiles $Inputs
if (-not $files -or $files.Count -eq 0) {
  throw "No .ndjson files found."
}

$rows = @(foreach ($file in $files) {
  Analyze-File -File $file -PreferredBus $Bus
})

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$csv = Join-Path $OutputDir "virtual_tsk_verification.csv"
$json = Join-Path $OutputDir "virtual_tsk_verification.json"
$rows | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8
$rows | ConvertTo-Json -Depth 5 | Set-Content -Path $json -Encoding UTF8

Write-Host "rows: $($rows.Count)"
Write-Host "csv: $csv"
Write-Host "json: $json"
