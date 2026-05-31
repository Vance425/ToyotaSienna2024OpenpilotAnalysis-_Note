#!/usr/bin/env python3
"""
Read-only Toyota SecOC frame capture helper.

This tool only receives CAN frames from Panda. It does not send CAN, UDS,
ISO-TP, or control messages. It is intended to collect enough sync and
protected frames from another 2024 Sienna to validate candidate SecOC keys.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


STOP = False
OPENPILOT_PROCESS_HINTS = ("boardd", "controlsd", "plannerd", "selfdrive.manager.manager", "manager.py")
DEFAULT_OPENPILOT_DIR = os.environ.get("OPENPILOT_DIR", "/data/openpilot")


def utc_now() -> str:
  return datetime.now(timezone.utc).isoformat()


def local_stamp() -> str:
  return datetime.now().strftime("%Y%m%d_%H%M%S")


def parse_int(value: str) -> int:
  return int(str(value).strip(), 0)


def parse_addr_list(values: Iterable[str] | None, default: list[int]) -> list[int]:
  if not values:
    return list(default)
  out: list[int] = []
  for value in values:
    for part in str(value).split(","):
      part = part.strip()
      if part:
        out.append(parse_int(part))
  return sorted(set(out))


def hex_data(data: bytes | bytearray) -> str:
  return bytes(data).hex()


def handle_stop(_signum, _frame) -> None:
  global STOP
  STOP = True


def command_output(cmd: list[str]) -> str:
  try:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, timeout=2)
  except Exception:
    return ""


def openpilot_running() -> dict:
  hits = []
  ps_text = command_output(["ps", "-eo", "pid=,args="])
  for line in ps_text.splitlines():
    stripped = line.strip()
    if not stripped:
      continue
    if any(hint in stripped for hint in OPENPILOT_PROCESS_HINTS):
      hits.append(stripped)
  return {"running": bool(hits), "matches": hits[:20]}


def load_panda():
  openpilot_dir = os.environ.get("OPENPILOT_DIR", DEFAULT_OPENPILOT_DIR)
  for path in (openpilot_dir, os.path.join(openpilot_dir, "panda", "python")):
    if path and path not in sys.path:
      sys.path.insert(0, path)
  try:
    from panda import Panda  # type: ignore
  except Exception as exc:
    raise SystemExit(
      "failed_to_import_panda: run this on C3X/openpilot environment or install panda Python package; "
      f"error={exc}"
    )
  return Panda


def set_safety_mode(panda, Panda, mode: str) -> dict:
  if mode == "none":
    return {"requested": mode, "attempted": False, "ok": True}

  mode_names = {
    "toyota": "SAFETY_TOYOTA",
    "silent": "SAFETY_SILENT",
    "nooutput": "SAFETY_NOOUTPUT",
    "elm327": "SAFETY_ELM327",
  }
  attr = mode_names[mode]
  safety_value = getattr(Panda, attr, None)
  if safety_value is None:
    return {"requested": mode, "attempted": False, "ok": False, "error": f"{attr}_missing"}

  try:
    panda.set_safety_mode(safety_value)
    return {"requested": mode, "attribute": attr, "value": int(safety_value), "attempted": True, "ok": True}
  except Exception as exc:
    return {"requested": mode, "attribute": attr, "attempted": True, "ok": False, "error": str(exc)}


class JsonlWriter:
  def __init__(self, path: Path):
    self.path = path
    self.fp = path.open("w", encoding="utf-8", newline="\n")

  def write(self, obj: dict) -> None:
    self.fp.write(json.dumps(obj, separators=(",", ":"), sort_keys=True) + "\n")

  def close(self) -> None:
    self.fp.close()


def write_json(path: Path, obj: dict) -> None:
  path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def frame_obj(ts_mono: float, ts_wall: float, seq: int, addr: int, data, bus: int) -> dict:
  return {
    "seq": seq,
    "ts_mono": round(ts_mono, 6),
    "ts_wall": round(ts_wall, 6),
    "bus": int(bus),
    "addr": int(addr),
    "addr_hex": f"0x{int(addr):x}",
    "data": hex_data(data),
    "dlc": len(data),
  }


def main() -> int:
  parser = argparse.ArgumentParser(description="Read-only capture of SecOC sync/protected CAN frames")
  parser.add_argument("--duration", type=float, default=120.0, help="seconds to capture; use 0 for until Ctrl+C")
  parser.add_argument("--output-dir", default="/data/secoc_frame_capture", help="root output directory")
  parser.add_argument("--target-addr", action="append", help="protected frame address, repeatable or comma-separated; default 0x2e4")
  parser.add_argument("--sync-addr", action="append", help="SecOC sync frame address, repeatable or comma-separated; default 0x0f")
  parser.add_argument("--bus", action="append", help="capture only these bus ids; default all")
  parser.add_argument("--safety-mode", choices=["toyota", "silent", "nooutput", "elm327", "none"], default="toyota")
  parser.add_argument("--allow-openpilot-running", action="store_true", help="do not refuse when boardd/openpilot processes are present")
  parser.add_argument("--no-save-all", action="store_true", help="only write sync/protected files, not all frames")
  parser.add_argument("--status-interval", type=float, default=1.0)
  args = parser.parse_args()

  signal.signal(signal.SIGINT, handle_stop)
  signal.signal(signal.SIGTERM, handle_stop)

  target_addrs = parse_addr_list(args.target_addr, [0x2E4])
  sync_addrs = parse_addr_list(args.sync_addr, [0x0F])
  buses = set(parse_addr_list(args.bus, [])) if args.bus else None

  op_status = openpilot_running()
  if op_status["running"] and not args.allow_openpilot_running:
    print("[ERROR] openpilot/boardd appears to be running. Stop openpilot first, or pass --allow-openpilot-running.")
    for line in op_status["matches"]:
      print(f"  {line}")
    return 2

  out_root = Path(args.output_dir)
  run_dir = out_root / f"secoc_frames_{local_stamp()}"
  run_dir.mkdir(parents=True, exist_ok=False)

  paths = {
    "metadata": run_dir / "metadata.json",
    "summary": run_dir / "summary.json",
    "all_jsonl": run_dir / "frames.jsonl",
    "all_csv": run_dir / "frames.csv",
    "sync_jsonl": run_dir / "sync_frames.jsonl",
    "protected_jsonl": run_dir / "protected_frames.jsonl",
    "probe_input": run_dir / "secoc_key_probe_input.json",
  }

  Panda = load_panda()
  panda = Panda()
  safety = set_safety_mode(panda, Panda, args.safety_mode)

  metadata = {
    "tool": "capture_secoc_frames.py",
    "created_utc": utc_now(),
    "duration_sec": args.duration,
    "target_addrs": [f"0x{x:x}" for x in target_addrs],
    "sync_addrs": [f"0x{x:x}" for x in sync_addrs],
    "buses": sorted(buses) if buses is not None else "all",
    "save_all": not args.no_save_all,
    "safety": safety,
    "openpilot_process_check": op_status,
    "note": "read-only capture; this script does not call can_send/isotp_send/UDS",
  }
  write_json(paths["metadata"], metadata)

  all_writer = None if args.no_save_all else JsonlWriter(paths["all_jsonl"])
  sync_writer = JsonlWriter(paths["sync_jsonl"])
  protected_writer = JsonlWriter(paths["protected_jsonl"])
  csv_fp = None
  csv_writer = None
  if not args.no_save_all:
    csv_fp = paths["all_csv"].open("w", newline="", encoding="utf-8")
    csv_writer = csv.DictWriter(csv_fp, fieldnames=["seq", "ts_mono", "ts_wall", "bus", "addr_hex", "addr", "dlc", "data"])
    csv_writer.writeheader()

  counts_by_bus: dict[str, int] = {}
  counts_by_addr: dict[str, int] = {}
  sync_frames: list[dict] = []
  protected_frames: list[dict] = []
  total = 0
  seq = 0
  can_recv_errors = 0
  start_mono = time.monotonic()
  end_mono = None if args.duration <= 0 else start_mono + args.duration
  last_status = 0.0

  print(f"[INFO] output={run_dir}")
  print(f"[INFO] target_addrs={[hex(x) for x in target_addrs]} sync_addrs={[hex(x) for x in sync_addrs]} buses={sorted(buses) if buses else 'all'}")
  print("[INFO] read-only capture started. Press Ctrl+C to stop.")

  try:
    try:
      panda.can_recv()
    except Exception:
      pass

    while not STOP:
      now = time.monotonic()
      if end_mono is not None and now >= end_mono:
        break

      try:
        msgs = panda.can_recv()
      except Exception as exc:
        can_recv_errors += 1
        if can_recv_errors <= 5:
          print(f"[WARN] can_recv error: {exc}")
        time.sleep(0.05)
        continue

      ts_mono = time.monotonic()
      ts_wall = time.time()
      for addr, data, bus in msgs:
        if buses is not None and int(bus) not in buses:
          continue

        seq += 1
        total += 1
        obj = frame_obj(ts_mono, ts_wall, seq, int(addr), data, int(bus))
        addr_hex = obj["addr_hex"]
        bus_key = str(int(bus))
        counts_by_bus[bus_key] = counts_by_bus.get(bus_key, 0) + 1
        counts_by_addr[addr_hex] = counts_by_addr.get(addr_hex, 0) + 1

        if all_writer:
          all_writer.write(obj)
        if csv_writer:
          csv_writer.writerow(obj)

        if int(addr) in sync_addrs:
          sync_writer.write(obj)
          if len(sync_frames) < 5000:
            sync_frames.append(obj)

        if int(addr) in target_addrs:
          protected_writer.write(obj)
          if len(protected_frames) < 5000:
            protected_frames.append(obj)

      if args.status_interval > 0 and ts_mono - last_status >= args.status_interval:
        last_status = ts_mono
        elapsed = ts_mono - start_mono
        print(
          f"[STATUS] {elapsed:6.1f}s total={total} "
          f"sync={sum(counts_by_addr.get(f'0x{x:x}', 0) for x in sync_addrs)} "
          f"protected={sum(counts_by_addr.get(f'0x{x:x}', 0) for x in target_addrs)}"
        )
  finally:
    if all_writer:
      all_writer.close()
    sync_writer.close()
    protected_writer.close()
    if csv_fp:
      csv_fp.close()

  finished_utc = utc_now()
  elapsed = time.monotonic() - start_mono
  summary = {
    "ok": True,
    "run_dir": str(run_dir),
    "started_utc": metadata["created_utc"],
    "finished_utc": finished_utc,
    "elapsed_sec": round(elapsed, 3),
    "total_frames": total,
    "sync_frame_count": sum(counts_by_addr.get(f"0x{x:x}", 0) for x in sync_addrs),
    "protected_frame_count": sum(counts_by_addr.get(f"0x{x:x}", 0) for x in target_addrs),
    "target_addrs": [f"0x{x:x}" for x in target_addrs],
    "sync_addrs": [f"0x{x:x}" for x in sync_addrs],
    "counts_by_bus": counts_by_bus,
    "top_addrs": sorted(counts_by_addr.items(), key=lambda item: item[1], reverse=True)[:50],
    "can_recv_errors": can_recv_errors,
    "files": {key: str(path) for key, path in paths.items() if path.exists()},
  }
  write_json(paths["summary"], summary)

  probe_input = {
    "metadata": metadata,
    "summary": summary,
    "sync_frames": sync_frames,
    "protected_frames": protected_frames,
    "truncated_note": "sync/protected arrays are capped at 5000 each; full streams are in jsonl files",
  }
  write_json(paths["probe_input"], probe_input)

  print("[DONE] capture finished")
  print(f"[DONE] output={run_dir}")
  print(f"[DONE] sync={summary['sync_frame_count']} protected={summary['protected_frame_count']} total={total}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
