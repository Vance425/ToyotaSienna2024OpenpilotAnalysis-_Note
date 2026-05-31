#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENPILOT_DIR="${OPENPILOT_DIR:-/data/openpilot}"
PYTHON_BIN="${PYTHON_BIN:-/usr/local/venv/bin/python3}"
STOP_OPENPILOT_SCRIPT="${STOP_OPENPILOT_SCRIPT:-${SCRIPT_DIR}/stop_openpilot.sh}"

STOP_OPENPILOT=0
FORCE_STOP_OPENPILOT=0
CAPTURE_ARGS=()

for arg in "$@"; do
  case "${arg}" in
    --stop-openpilot)
      STOP_OPENPILOT=1
      ;;
    --force-stop-openpilot)
      STOP_OPENPILOT=1
      FORCE_STOP_OPENPILOT=1
      ;;
    *)
      CAPTURE_ARGS+=("${arg}")
      ;;
  esac
done

if [[ -f "${OPENPILOT_DIR}/launch_env.sh" ]]; then
  # shellcheck disable=SC1091
  set +u
  source "${OPENPILOT_DIR}/launch_env.sh"
  set -u
fi

export OPENPILOT_DIR
export PYTHONPATH="${OPENPILOT_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

if [[ "${STOP_OPENPILOT}" = "1" ]]; then
  if [[ ! -x "${STOP_OPENPILOT_SCRIPT}" ]]; then
    echo "[ERROR] stop_openpilot script not executable: ${STOP_OPENPILOT_SCRIPT}" >&2
    exit 2
  fi
  echo "[INFO] stopping openpilot before SecOC frame capture"
  if [[ "${FORCE_STOP_OPENPILOT}" = "1" ]]; then
    MY_SIENNA_STOP_OPENPILOT_FORCE=1 "${STOP_OPENPILOT_SCRIPT}"
  else
    "${STOP_OPENPILOT_SCRIPT}"
  fi
fi

exec "${PYTHON_BIN}" "${SCRIPT_DIR}/capture_secoc_frames.py" "${CAPTURE_ARGS[@]}"
