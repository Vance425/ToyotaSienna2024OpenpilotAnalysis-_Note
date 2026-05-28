#!/usr/bin/env bash
set -euo pipefail

PYTHON_CMD="${PYTHON_CMD:-python3}"
SCRIPT_PATH="<LOCAL_ANALYSIS_WORKSPACE>/scripts/control_model_v22.py"
EMIT_ONLY="${EMIT_ONLY:-0}"

if [ "$#" -gt 0 ]; then
  PRESETS=("$@")
else
  PRESETS=(
    "0311_band_b_b6b7"
    "0316_forward_lowband_b6b7"
    "0316_forward_promoted_b4b5"
    "0316_reverse_core_b6b7"
  )
fi

run_preset() {
  local preset="$1"
  local input_dir output_dir
  local -a args

  case "$preset" in
    0311_band_b_b6b7)
      input_dir="<LOCAL_TEMP_WSL>/toyota_v1/_control_model_v22_safe"
      output_dir="<LOCAL_TEMP_WSL>/toyota_v1/_control_model_v22_safe/v22_out_0311_band_b_b6b7"
      args=(
        "--feedback-signal" "s16be_b6_7"
        "--label" "0311_band_b_b6b7"
        "--control-index-min" "2641"
        "--control-index-max" "2832"
      )
      ;;
    0316_forward_lowband_b6b7)
      input_dir="<LOCAL_TEMP_WSL>/toyota_v1/_control_model_v22_safe_2"
      output_dir="<LOCAL_TEMP_WSL>/toyota_v1/_control_model_v22_safe_2/v22_out_0316_forward_lowband_b6b7"
      args=(
        "--feedback-signal" "s16be_b6_7"
        "--label" "0316_forward_lowband_b6b7"
        "--domain" "positive_or_forward"
        "--b5-s8" "0"
        "--b5-s8" "1"
      )
      ;;
    0316_forward_promoted_b4b5)
      input_dir="<LOCAL_TEMP_WSL>/toyota_v1/_control_model_v22_safe_2"
      output_dir="<LOCAL_TEMP_WSL>/toyota_v1/_control_model_v22_safe_2/v22_out_0316_forward_promoted_b4b5"
      args=(
        "--feedback-signal" "s16le_b4_5"
        "--label" "0316_forward_promoted_b4b5"
        "--domain" "positive_or_forward"
        "--b5-s8" "3"
        "--b5-s8" "4"
        "--b5-s8" "5"
        "--b5-s8" "6"
      )
      ;;
    0316_reverse_core_b6b7)
      input_dir="<LOCAL_TEMP_WSL>/toyota_v1/_control_model_v22_safe_2"
      output_dir="<LOCAL_TEMP_WSL>/toyota_v1/_control_model_v22_safe_2/v22_out_0316_reverse_core_b6b7"
      args=(
        "--feedback-signal" "s16be_b6_7"
        "--label" "0316_reverse_core_b6b7"
        "--domain" "negative_or_reverse"
        "--b5-s8" "-1"
        "--b5-s8" "-2"
        "--b5-s8" "-3"
      )
      ;;
    *)
      echo "Unknown preset: $preset" >&2
      return 1
      ;;
  esac

  if [ "$EMIT_ONLY" = "1" ]; then
    echo "[$preset]"
    printf '%q ' "$PYTHON_CMD" "$SCRIPT_PATH" "$input_dir" "--output-dir" "$output_dir" "${args[@]}"
    echo
    echo
    return 0
  fi

  echo "Running preset: $preset"
  "$PYTHON_CMD" "$SCRIPT_PATH" "$input_dir" "--output-dir" "$output_dir" "${args[@]}"
}

for preset in "${PRESETS[@]}"; do
  run_preset "$preset"
done
