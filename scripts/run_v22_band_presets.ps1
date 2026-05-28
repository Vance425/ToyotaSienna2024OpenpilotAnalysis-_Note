param(
  [string]$PythonCmd = "python",
  [string[]]$Presets = @("0311_band_b_b6b7", "0316_forward_lowband_b6b7", "0316_forward_promoted_b4b5", "0316_reverse_core_b6b7"),
  [switch]$EmitOnly
)

$ScriptPath = "<LOCAL_ANALYSIS_WORKSPACE>\scripts\control_model_v22.py"

$PresetMap = @{
  "0311_band_b_b6b7" = @{
    InputDir = "<LOCAL_TEMP>\toyota_v1\_control_model_v22_safe"
    OutputDir = "<LOCAL_TEMP>\toyota_v1\_control_model_v22_safe\v22_out_0311_band_b_b6b7"
    Args = @(
      "--feedback-signal", "s16be_b6_7",
      "--label", "0311_band_b_b6b7",
      "--control-index-min", "2641",
      "--control-index-max", "2832"
    )
  }
  "0316_forward_lowband_b6b7" = @{
    InputDir = "<LOCAL_TEMP>\toyota_v1\_control_model_v22_safe_2"
    OutputDir = "<LOCAL_TEMP>\toyota_v1\_control_model_v22_safe_2\v22_out_0316_forward_lowband_b6b7"
    Args = @(
      "--feedback-signal", "s16be_b6_7",
      "--label", "0316_forward_lowband_b6b7",
      "--domain", "positive_or_forward",
      "--b5-s8", "0",
      "--b5-s8", "1"
    )
  }
  "0316_forward_promoted_b4b5" = @{
    InputDir = "<LOCAL_TEMP>\toyota_v1\_control_model_v22_safe_2"
    OutputDir = "<LOCAL_TEMP>\toyota_v1\_control_model_v22_safe_2\v22_out_0316_forward_promoted_b4b5"
    Args = @(
      "--feedback-signal", "s16le_b4_5",
      "--label", "0316_forward_promoted_b4b5",
      "--domain", "positive_or_forward",
      "--b5-s8", "3",
      "--b5-s8", "4",
      "--b5-s8", "5",
      "--b5-s8", "6"
    )
  }
  "0316_reverse_core_b6b7" = @{
    InputDir = "<LOCAL_TEMP>\toyota_v1\_control_model_v22_safe_2"
    OutputDir = "<LOCAL_TEMP>\toyota_v1\_control_model_v22_safe_2\v22_out_0316_reverse_core_b6b7"
    Args = @(
      "--feedback-signal", "s16be_b6_7",
      "--label", "0316_reverse_core_b6b7",
      "--domain", "negative_or_reverse",
      "--b5-s8", "-1",
      "--b5-s8", "-2",
      "--b5-s8", "-3"
    )
  }
}

foreach ($preset in $Presets) {
  if (-not $PresetMap.ContainsKey($preset)) {
    throw "Unknown preset: $preset"
  }

  $config = $PresetMap[$preset]
  $cmdArgs = @(
    $ScriptPath,
    $config.InputDir,
    "--output-dir", $config.OutputDir
  ) + $config.Args

  if ($EmitOnly) {
    Write-Host "[$preset]"
    Write-Host ($PythonCmd + " " + ($cmdArgs -join " "))
    Write-Host ""
    continue
  }

  Write-Host "Running preset: $preset"
  & $PythonCmd @cmdArgs
  if ($LASTEXITCODE -ne 0) {
    throw "Preset failed: $preset"
  }
}
