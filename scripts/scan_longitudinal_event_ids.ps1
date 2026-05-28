param(
  [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
  [string[]]$Inputs,
  [string]$OutputDir = "<LOCAL_ANALYSIS_WORKSPACE>\analysis-output\longitudinal_event_scan",
  [int]$Bus = 0,
  [int]$ControlDeltaThreshold = 100
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

function Make-Record {
  param([int64]$Ts, [string]$Value)
  return [pscustomobject]@{
    ts_ms = $Ts
    value = $Value
  }
}

function Find-WindowChanged {
  param([object[]]$Series, [int64]$Ts, [int64]$WindowBefore, [int64]$WindowAfter)
  if ($Series.Count -eq 0) { return $null }
  foreach ($rec in $Series) {
    if ($rec.ts_ms -lt ($Ts - $WindowBefore)) { continue }
    if ($rec.ts_ms -gt ($Ts + $WindowAfter)) { break }
    if ($rec.changed) { return $rec }
  }
  return $null
}

function Prepare-ChangeSeries {
  param([System.Collections.Generic.List[object]]$Series)
  $arr = $Series.ToArray()
  if ($arr.Count -eq 0) { return $arr }
  $prev = $null
  foreach ($rec in $arr) {
    if ($null -eq $prev) {
      Add-Member -InputObject $rec -NotePropertyName changed -NotePropertyValue $false -Force
    } else {
      Add-Member -InputObject $rec -NotePropertyName changed -NotePropertyValue ($rec.value -ne $prev.value) -Force
    }
    $prev = $rec
  }
  return $arr
}

function Analyze-File {
  param([System.IO.FileInfo]$File, [int]$PreferredBus, [int]$Threshold)

  $s260 = New-Object System.Collections.Generic.List[object]
  $cand = @{
    "0xAA"  = New-Object System.Collections.Generic.List[object]
    "0x90"  = New-Object System.Collections.Generic.List[object]
    "0x127" = New-Object System.Collections.Generic.List[object]
    "0x371" = New-Object System.Collections.Generic.List[object]
    "0x191" = New-Object System.Collections.Generic.List[object]
    "0x101" = New-Object System.Collections.Generic.List[object]
    "0x108" = New-Object System.Collections.Generic.List[object]
    "0x116" = New-Object System.Collections.Generic.List[object]
    "0x131" = New-Object System.Collections.Generic.List[object]
    "0x2E4" = New-Object System.Collections.Generic.List[object]
    "0xD8"  = New-Object System.Collections.Generic.List[object]
  }

  Get-Content $File.FullName | ForEach-Object {
    $line = $_.Trim()
    if (-not $line) { return }
    try { $o = $line | ConvertFrom-Json } catch { return }
    if ([int]$o.bus -ne $PreferredBus) { return }
    $addr = [int]$o.addr
    $ts = [int64]$o.ts_ms
    $hex = [string]$o.data
    try { $buf = Parse-HexBytes $hex } catch { return }

    switch ($addr) {
      0x260 {
        if ($buf.Length -ge 8) {
          $s260.Add([pscustomobject]@{
              ts_ms = $ts
              control = [double](Get-ControlFrom260 $buf)
            })
        }
      }
      0xAA {
        if ($buf.Length -ge 1) { $cand["0xAA"].Add((Make-Record $ts ("{0}" -f $buf[0]))) }
      }
      0x90 {
        if ($buf.Length -ge 2) { $cand["0x90"].Add((Make-Record $ts ("{0}" -f (Get-S16BE $buf 0)))) }
      }
      0x127 {
        if ($buf.Length -ge 2) { $cand["0x127"].Add((Make-Record $ts ("{0}" -f (Get-S16BE $buf 0)))) }
      }
      0x371 {
        if ($buf.Length -ge 4) { $cand["0x371"].Add((Make-Record $ts ("be:{0}|le:{1}" -f (Get-S16BE $buf 2), (Get-S16LE $buf 2)))) }
      }
      0x191 {
        if ($buf.Length -ge 8) { $cand["0x191"].Add((Make-Record $ts ("b45:{0}|b67:{1}" -f (Get-S16LE $buf 4), (Get-S16BE $buf 6)))) }
      }
      0x101 { $cand["0x101"].Add((Make-Record $ts $hex)) }
      0x108 { $cand["0x108"].Add((Make-Record $ts $hex)) }
      0x116 {
        if ($buf.Length -ge 2) { $cand["0x116"].Add((Make-Record $ts ("phase:{0:x2}{1:x2}|raw:{2}" -f $buf[0], $buf[1], $hex))) }
      }
      0x131 {
        if ($buf.Length -ge 4) { $cand["0x131"].Add((Make-Record $ts ("fam:{0:x2}{1:x2}|raw:{2}" -f $buf[2], $buf[3], $hex))) }
      }
      0x2E4 { $cand["0x2E4"].Add((Make-Record $ts $hex)) }
      0x0D8 { $cand["0xD8"].Add((Make-Record $ts $hex)) }
    }
  }

  $s260Arr = $s260.ToArray()
  $events = New-Object System.Collections.Generic.List[object]
  for ($i = 1; $i -lt $s260Arr.Count; $i++) {
    $delta = $s260Arr[$i].control - $s260Arr[$i - 1].control
    if ([Math]::Abs($delta) -ge $Threshold) {
      $events.Add([pscustomobject]@{
          sample_id = $File.BaseName
          sample_path = $File.FullName
          ts_ms = $s260Arr[$i].ts_ms
          control = [Math]::Round($s260Arr[$i].control, 3)
          delta_control = [Math]::Round($delta, 3)
          event_type = if ($delta -gt 0) { "accel_like" } else { "brake_like" }
        })
    }
  }

  $seriesMap = @{}
  foreach ($k in $cand.Keys) {
    $seriesMap[$k] = Prepare-ChangeSeries $cand[$k]
  }

  $detailRows = New-Object System.Collections.Generic.List[object]
  foreach ($ev in $events) {
    foreach ($k in $seriesMap.Keys) {
      $rec = Find-WindowChanged $seriesMap[$k] $ev.ts_ms 20 50
      $detailRows.Add([pscustomobject]@{
          sample_id = $ev.sample_id
          sample_path = $ev.sample_path
          ts_ms = $ev.ts_ms
          event_type = $ev.event_type
          control = $ev.control
          delta_control = $ev.delta_control
          candidate_id = $k
          changed_in_window = if ($null -eq $rec) { 0 } else { 1 }
          candidate_value = if ($null -eq $rec) { "" } else { $rec.value }
          candidate_ts_ms = if ($null -eq $rec) { "" } else { $rec.ts_ms }
        })
    }
  }

  $summaryRows = New-Object System.Collections.Generic.List[object]
  foreach ($etype in @("accel_like", "brake_like")) {
    $etypeRows = $detailRows | Where-Object { $_.event_type -eq $etype }
    $eventCount = ($events | Where-Object { $_.event_type -eq $etype }).Count
    foreach ($k in $seriesMap.Keys) {
      $kr = $etypeRows | Where-Object { $_.candidate_id -eq $k }
      $changed = ($kr | Where-Object { $_.changed_in_window -eq 1 }).Count
      $summaryRows.Add([pscustomobject]@{
          sample_id = $File.BaseName
          sample_path = $File.FullName
          event_type = $etype
          event_count = $eventCount
          candidate_id = $k
          changed_event_count = $changed
          changed_ratio = if ($eventCount -eq 0) { "" } else { [Math]::Round($changed / $eventCount, 3) }
        })
    }
  }

  return [pscustomobject]@{
    detail = $detailRows
    summary = $summaryRows
  }
}

$files = Get-NdjsonFiles $Inputs
if (-not $files -or $files.Count -eq 0) {
  throw "No .ndjson files found."
}

$allDetail = New-Object System.Collections.Generic.List[object]
$allSummary = New-Object System.Collections.Generic.List[object]
foreach ($file in $files) {
  $r = Analyze-File -File $file -PreferredBus $Bus -Threshold $ControlDeltaThreshold
  foreach ($d in $r.detail) { $allDetail.Add($d) }
  foreach ($s in $r.summary) { $allSummary.Add($s) }
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$detailCsv = Join-Path $OutputDir "longitudinal_event_detail.csv"
$summaryCsv = Join-Path $OutputDir "longitudinal_event_summary.csv"
$allDetail | Export-Csv -Path $detailCsv -NoTypeInformation -Encoding UTF8
$allSummary | Export-Csv -Path $summaryCsv -NoTypeInformation -Encoding UTF8

Write-Host "detail rows: $($allDetail.Count)"
Write-Host "summary rows: $($allSummary.Count)"
Write-Host "detail csv: $detailCsv"
Write-Host "summary csv: $summaryCsv"
