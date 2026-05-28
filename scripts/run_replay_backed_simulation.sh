#!/usr/bin/env bash
set -euo pipefail

PYTHON_CMD="${PYTHON_CMD:-python3}"
SCRIPT_PATH="<LOCAL_ANALYSIS_WORKSPACE>/scripts/replay_backed_simulation.py"
OUTPUT_DIR="${OUTPUT_DIR:-<LOCAL_ANALYSIS_WORKSPACE>/analysis-output/replay_simulation}"
EMIT_ONLY="${EMIT_ONLY:-0}"

if [ "$#" -gt 0 ]; then
  SLEW_LIMITS=("$@")
else
  SLEW_LIMITS=("10" "25" "50" "75" "100")
fi

ARGS=(
  "$SCRIPT_PATH"
  "--output-dir" "$OUTPUT_DIR"
)

for limit in "${SLEW_LIMITS[@]}"; do
  ARGS+=("--slew" "$limit")
done

if [ "$EMIT_ONLY" = "1" ]; then
  printf '%q ' "$PYTHON_CMD" "${ARGS[@]}"
  echo
  exit 0
fi

echo "Running replay-backed simulation harness"
"$PYTHON_CMD" "${ARGS[@]}"
