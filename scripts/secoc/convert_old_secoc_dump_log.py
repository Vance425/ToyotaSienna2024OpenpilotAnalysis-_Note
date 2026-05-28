#!/usr/bin/env python3
"""Rebuild a raw dump .bin from the old SecOC tool terminal log.

The old tool prints payload-return frames like:

  --addr-- 1961
  ----data---- b'\\x074n\\xbe\\x00\\x00\\x00\\x00'
  07346ebe00000000

The first byte is the payload response marker. Bytes 1..3 are the low
24-bit memory address in little-endian order, and bytes 4..7 are the
four dumped bytes for that address.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FRAME_RE = re.compile(r"^[0-9a-fA-F]{16}$")


def parse_int(value: str) -> int:
  return int(value, 0)


def parse_frames(text: str, base_high: int) -> dict[int, bytes]:
  frames: dict[int, bytes] = {}
  in_dump = False
  for raw_line in text.splitlines():
    line = raw_line.strip()
    if "Dumping keys" in line:
      in_dump = True
      continue
    if not in_dump:
      continue
    if not FRAME_RE.match(line):
      continue

    raw = bytes.fromhex(line)
    if len(raw) != 8 or raw[0] != 0x07:
      continue
    low24 = int.from_bytes(raw[1:4], "little")
    addr = base_high | low24
    frames[addr] = raw[4:8]
  return frames


def rebuild(frames: dict[int, bytes], start: int | None, end: int | None) -> tuple[int, int, bytes, list[int]]:
  if not frames:
    raise RuntimeError("no old dump frames found")

  frame_addrs = sorted(frames)
  actual_start = start if start is not None else frame_addrs[0]
  actual_end = end if end is not None else frame_addrs[-1] + 4
  if actual_end <= actual_start:
    raise RuntimeError("end address must be greater than start address")
  if (actual_end - actual_start) % 4 != 0:
    raise RuntimeError("range length must be divisible by 4")

  missing = [addr for addr in range(actual_start, actual_end, 4) if addr not in frames]
  out = bytearray()
  for addr in range(actual_start, actual_end, 4):
    out += frames.get(addr, b"\x00" * 4)
  return actual_start, actual_end, bytes(out), missing


def main() -> int:
  parser = argparse.ArgumentParser(description="Convert old SecOC terminal dump log to raw .bin")
  parser.add_argument("log", type=Path)
  parser.add_argument("--output", "-o", type=Path, required=True)
  parser.add_argument("--summary", type=Path)
  parser.add_argument("--start", type=parse_int)
  parser.add_argument("--end", type=parse_int)
  parser.add_argument("--base-high", type=parse_int, default=0xFE000000)
  args = parser.parse_args()

  text = args.log.read_text(encoding="utf-8", errors="replace")
  frames = parse_frames(text, args.base_high)
  start, end, data, missing = rebuild(frames, args.start, args.end)

  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_bytes(data)

  summary = {
    "input": str(args.log),
    "output": str(args.output),
    "start": f"0x{start:08x}",
    "end": f"0x{end:08x}",
    "bytes": len(data),
    "frames_found_total": len(frames),
    "frames_expected": (end - start) // 4,
    "missing_frames": len(missing),
    "missing_addresses": [f"0x{addr:08x}" for addr in missing[:64]],
    "nonzero_bytes": sum(1 for b in data if b != 0),
  }

  if args.summary:
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

  print(json.dumps(summary, indent=2, sort_keys=True))
  return 1 if missing else 0


if __name__ == "__main__":
  raise SystemExit(main())
