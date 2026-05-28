#!/usr/bin/env python3
"""
Compare multiple SecOC dump runs offline.

This tool does not connect to a car and does not write openpilot params. It
compares raw dump bytes across runs to separate stable material from changing
state, freshness, counters, or wrong/empty regions.
"""

import argparse
import csv
import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_KEY_SIZE = 16
OLD_KEY_OFFSET = 0x0C
OLD_CHECKSUM_OFFSET = 0x1D


@dataclass
class DumpEntry:
  run_label: str
  run_dir: str
  dump_path: str
  dump_name: str
  group_key: str
  range_start: str | None
  range_end: str | None
  size: int
  sha256: str
  metadata_path: str | None


@dataclass
class StableCandidate:
  group_key: str
  offset: str
  absolute_address: str | None
  candidate_hex: str
  entropy: float
  unique_bytes: int
  zero_bytes: int
  ff_bytes: int
  run_count: int
  old_checksum_all: bool
  score: float
  notes: str


@dataclass
class VariableRegion:
  group_key: str
  offset: str
  absolute_address: str | None
  size: int
  changed_bytes: int
  changed_ratio: float
  unique_window_values: int
  per_run_sha256_16: str
  classification: str
  notes: str


def parse_int(text: str) -> int:
  return int(str(text), 0)


def sha256_bytes(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


def entropy(data: bytes) -> float:
  if not data:
    return 0.0
  counts = {}
  for b in data:
    counts[b] = counts.get(b, 0) + 1
  total = len(data)
  return -sum((count / total) * math.log2(count / total) for count in counts.values())


def parse_range_from_name(path: Path) -> tuple[int | None, int | None]:
  matches = re.findall(r"([0-9a-fA-F]{8})", path.stem)
  if len(matches) >= 2:
    return int(matches[-2], 16), int(matches[-1], 16)
  return None, None


def find_metadata_near(path: Path) -> Path | None:
  candidates = sorted(path.parent.glob("metadata*.json"))
  return candidates[0] if candidates else None


def load_metadata(path: Path | None) -> dict:
  if not path or not path.exists():
    return {}
  try:
    return json.loads(path.read_text(encoding="utf-8"))
  except Exception:
    return {}


def range_from_metadata(dump_path: Path, metadata: dict) -> tuple[int | None, int | None]:
  for item in metadata.get("dumps", []) or []:
    if item.get("file") == dump_path.name:
      try:
        return parse_int(item.get("start")), parse_int(item.get("end"))
      except Exception:
        pass
  return parse_range_from_name(dump_path)


def run_label_from_dir(path: Path) -> str:
  for part in reversed(path.parts):
    if part:
      return part
  return str(path)


def group_key_for(dump_path: Path, range_start: int | None, range_end: int | None) -> str:
  if range_start is not None and range_end is not None:
    return f"{range_start:08x}_{range_end:08x}"
  stem = dump_path.stem
  stem = re.sub(r"^dump_?", "", stem)
  stem = re.sub(r"\d{8}_\d{6}_?", "", stem)
  return stem or dump_path.name


def discover_entries(inputs: list[str]) -> list[DumpEntry]:
  entries: list[DumpEntry] = []
  for raw in inputs:
    root = Path(raw).expanduser().resolve()
    if root.is_file() and root.suffix.lower() == ".bin":
      dump_paths = [root]
      run_dir = root.parent
    elif root.is_dir():
      dump_paths = sorted(root.rglob("dump*.bin"))
      run_dir = root
    else:
      continue
    for dump_path in dump_paths:
      metadata_path = find_metadata_near(dump_path)
      metadata = load_metadata(metadata_path)
      range_start, range_end = range_from_metadata(dump_path, metadata)
      data = dump_path.read_bytes()
      entries.append(DumpEntry(
        run_label=run_label_from_dir(run_dir),
        run_dir=str(run_dir),
        dump_path=str(dump_path),
        dump_name=dump_path.name,
        group_key=group_key_for(dump_path, range_start, range_end),
        range_start=f"0x{range_start:08x}" if range_start is not None else None,
        range_end=f"0x{range_end:08x}" if range_end is not None else None,
        size=len(data),
        sha256=sha256_bytes(data),
        metadata_path=str(metadata_path) if metadata_path else None,
      ))
  return entries


def checksum_hit_for_struct(struct: bytes, checksum_offset: int = OLD_CHECKSUM_OFFSET) -> bool:
  if checksum_offset >= len(struct):
    return False
  checksum = (~sum(struct[:checksum_offset])) & 0xFF
  return checksum == struct[checksum_offset]


def old_checksum_ok(data: bytes, candidate_offset: int) -> bool:
  if candidate_offset >= OLD_KEY_OFFSET:
    start = candidate_offset - OLD_KEY_OFFSET
    struct = data[start:start + 0x20]
    if len(struct) == 0x20 and checksum_hit_for_struct(struct):
      return True
  start = (candidate_offset // 0x20) * 0x20
  struct = data[start:start + 0x20]
  return len(struct) == 0x20 and checksum_hit_for_struct(struct)


def old_key_offset_ok(data: bytes, candidate_offset: int) -> bool:
  if candidate_offset < OLD_KEY_OFFSET:
    return False
  start = candidate_offset - OLD_KEY_OFFSET
  if start % 0x20 != 0:
    return False
  struct = data[start:start + 0x20]
  return len(struct) == 0x20 and checksum_hit_for_struct(struct)


def absolute_addr(range_start: int | None, offset: int) -> str | None:
  if range_start is None:
    return None
  return f"0x{range_start + offset:08x}"


def byte_change_summary(datas: list[bytes]) -> dict:
  size = min(len(data) for data in datas)
  changed_offsets = []
  stable_nonzero = 0
  stable_zero = 0
  stable_ff = 0
  for offset in range(size):
    vals = {data[offset] for data in datas}
    if len(vals) > 1:
      changed_offsets.append(offset)
    else:
      val = next(iter(vals))
      if val == 0:
        stable_zero += 1
      elif val == 0xFF:
        stable_ff += 1
      else:
        stable_nonzero += 1
  return {
    "size_compared": size,
    "changed_byte_count": len(changed_offsets),
    "changed_ratio": round(len(changed_offsets) / size, 6) if size else 0,
    "stable_nonzero_count": stable_nonzero,
    "stable_zero_count": stable_zero,
    "stable_ff_count": stable_ff,
    "changed_ranges": compact_ranges(changed_offsets)[:80],
  }


def compact_ranges(offsets: list[int]) -> list[str]:
  if not offsets:
    return []
  ranges = []
  start = prev = offsets[0]
  for offset in offsets[1:]:
    if offset == prev + 1:
      prev = offset
      continue
    ranges.append(f"0x{start:04x}" if start == prev else f"0x{start:04x}-0x{prev:04x}")
    start = prev = offset
  ranges.append(f"0x{start:04x}" if start == prev else f"0x{start:04x}-0x{prev:04x}")
  return ranges


def classify_window(values: list[bytes], changed_bytes: int) -> tuple[str, str]:
  unique_count = len(set(values))
  size = len(values[0]) if values else 0
  if unique_count == 1:
    value = values[0]
    if value == b"\x00" * size:
      return "stable_zero", "probably empty/uninitialized or wrong range"
    if value == b"\xff" * size:
      return "stable_ff", "probably erased/fill pattern"
    return "stable", "stable across runs"
  if unique_count == len(values):
    return "all_runs_unique", "possible freshness/session state/random/counter material"
  if changed_bytes <= max(1, size // 4):
    return "partially_changing", "possible counter/status field near stable material"
  return "mixed", "some runs share values and some differ"


def stable_candidate_score(chunk: bytes, run_count: int, checksum_all: bool, old_key_offset_all: bool, offset: int) -> float:
  if chunk == b"\x00" * len(chunk) or chunk == b"\xff" * len(chunk):
    return -100.0
  score = entropy(chunk) * 20.0
  score += min(len(set(chunk)), 16) * 1.5
  score += min(run_count, 10) * 2.0
  if checksum_all:
    score += 30.0
  if old_key_offset_all:
    score += 35.0
  if offset % 16 == 0:
    score += 8.0
  if offset % 4 == 0:
    score += 2.0
  if chunk.count(0) >= 8 or chunk.count(0xFF) >= 8:
    score -= 35.0
  return round(score, 3)


def scan_stable_candidates(
  group_key: str,
  datas: list[bytes],
  range_start: int | None,
  min_entropy: float,
  stride: int,
  top: int,
) -> list[StableCandidate]:
  size = min(len(data) for data in datas)
  candidates: list[StableCandidate] = []
  for offset in range(0, max(0, size - DEFAULT_KEY_SIZE + 1), stride):
    values = [data[offset:offset + DEFAULT_KEY_SIZE] for data in datas]
    if len(set(values)) != 1:
      continue
    chunk = values[0]
    if chunk == b"\x00" * DEFAULT_KEY_SIZE or chunk == b"\xff" * DEFAULT_KEY_SIZE:
      continue
    ent = entropy(chunk)
    checksum_all = all(old_checksum_ok(data, offset) for data in datas)
    key_offset_all = all(old_key_offset_ok(data, offset) for data in datas)
    if ent < min_entropy and not checksum_all:
      continue
    notes = []
    if checksum_all:
      notes.append("old_checksum_all")
    if key_offset_all:
      notes.append("old_key_offset_all")
    if offset % 16 == 0:
      notes.append("aligned16")
    if ent >= 3.25 and len(set(chunk)) >= 10:
      notes.append("key_like_entropy")
    score = stable_candidate_score(chunk, len(datas), checksum_all, key_offset_all, offset)
    candidates.append(StableCandidate(
      group_key=group_key,
      offset=f"0x{offset:04x}",
      absolute_address=absolute_addr(range_start, offset),
      candidate_hex=chunk.hex(),
      entropy=round(ent, 4),
      unique_bytes=len(set(chunk)),
      zero_bytes=chunk.count(0),
      ff_bytes=chunk.count(0xFF),
      run_count=len(datas),
      old_checksum_all=checksum_all,
      score=score,
      notes=";".join(notes),
    ))
  candidates.sort(key=lambda c: c.score, reverse=True)
  return candidates[:top]


def scan_variable_regions(
  group_key: str,
  datas: list[bytes],
  range_start: int | None,
  window: int,
  step: int,
  top: int,
) -> list[VariableRegion]:
  size = min(len(data) for data in datas)
  regions: list[VariableRegion] = []
  for offset in range(0, max(0, size - window + 1), step):
    values = [data[offset:offset + window] for data in datas]
    changed = 0
    for i in range(window):
      if len({value[i] for value in values}) > 1:
        changed += 1
    classification, notes = classify_window(values, changed)
    if classification in ("stable_zero", "stable_ff", "stable"):
      continue
    hashes = ",".join(sha256_bytes(value)[:16] for value in values)
    regions.append(VariableRegion(
      group_key=group_key,
      offset=f"0x{offset:04x}",
      absolute_address=absolute_addr(range_start, offset),
      size=window,
      changed_bytes=changed,
      changed_ratio=round(changed / window, 4) if window else 0,
      unique_window_values=len(set(values)),
      per_run_sha256_16=hashes,
      classification=classification,
      notes=notes,
    ))
  regions.sort(key=lambda r: (r.changed_ratio, r.unique_window_values), reverse=True)
  return regions[:top]


def write_csv(path: Path, rows: list, fieldnames: list[str]) -> None:
  with path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
      writer.writerow(asdict(row) if hasattr(row, "__dataclass_fields__") else row)


def write_report(path: Path, summary: dict, stable: list[StableCandidate], variable: list[VariableRegion]) -> None:
  lines = [
    "# SecOC Dump Run Compare Report",
    "",
    f"Generated: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
    "",
    "This is an offline stability comparison. Stable candidates are not proof of a valid Toyota Sienna 2024 SecOC/TSK key.",
    "",
    "## Groups",
    "",
  ]
  for group_key, info in summary.get("groups", {}).items():
    compare = info.get("compare", {})
    lines.append(f"### `{group_key}`")
    lines.append(f"- runs: `{len(info.get('entries', []))}`")
    lines.append(f"- size compared: `{compare.get('size_compared')}`")
    lines.append(f"- changed bytes: `{compare.get('changed_byte_count')}`")
    lines.append(f"- changed ratio: `{compare.get('changed_ratio')}`")
    lines.append(f"- stable non-zero bytes: `{compare.get('stable_nonzero_count')}`")
    lines.append(f"- stable zero bytes: `{compare.get('stable_zero_count')}`")
    if compare.get("changed_ranges"):
      lines.append(f"- changed ranges: `{', '.join(compare.get('changed_ranges', [])[:16])}`")
    lines.append("")

  lines.extend(["## Top Stable Candidates", ""])
  if not stable:
    lines.append("No stable candidates matched the threshold.")
  else:
    lines.append("| rank | group | offset | absolute | score | entropy | old checksum all | candidate | notes |")
    lines.append("|---:|---|---:|---:|---:|---:|---|---|---|")
    for idx, item in enumerate(stable[:50], 1):
      lines.append(
        f"| {idx} | `{item.group_key}` | `{item.offset}` | `{item.absolute_address or ''}` | "
        f"`{item.score}` | `{item.entropy}` | `{item.old_checksum_all}` | `{item.candidate_hex}` | `{item.notes}` |"
      )

  lines.extend(["", "## Top Variable Regions", ""])
  if not variable:
    lines.append("No variable regions found.")
  else:
    lines.append("| rank | group | offset | absolute | changed ratio | unique values | class | notes |")
    lines.append("|---:|---|---:|---:|---:|---:|---|---|")
    for idx, item in enumerate(variable[:50], 1):
      lines.append(
        f"| {idx} | `{item.group_key}` | `{item.offset}` | `{item.absolute_address or ''}` | "
        f"`{item.changed_ratio}` | `{item.unique_window_values}` | `{item.classification}` | `{item.notes}` |"
      )
  path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Compare multiple Sienna 2024 SecOC dump runs offline")
  parser.add_argument("inputs", nargs="+", help="dump run directories or dump .bin files")
  parser.add_argument("--output-dir", help="output directory; default: compare_out_YYYYMMDD_HHMMSS")
  parser.add_argument("--min-entropy", type=float, default=2.75, help="minimum entropy for stable 16-byte candidates without checksum")
  parser.add_argument("--stride", type=int, default=4, help="stable candidate scan stride")
  parser.add_argument("--top-stable", type=int, default=120, help="max stable candidates per group before global sort")
  parser.add_argument("--global-top-stable", type=int, default=250, help="max stable candidates written globally")
  parser.add_argument("--window", type=int, default=32, help="variable region window size")
  parser.add_argument("--window-step", type=int, default=8, help="variable region window step")
  parser.add_argument("--top-variable", type=int, default=80, help="max variable regions per group before global sort")
  parser.add_argument("--global-top-variable", type=int, default=200, help="max variable regions written globally")
  return parser


def main() -> None:
  args = build_arg_parser().parse_args()
  if len(args.inputs) < 2:
    raise SystemExit("provide at least two dump runs or dump files")
  for name in ("stride", "window", "window_step", "top_stable", "top_variable"):
    if getattr(args, name) <= 0:
      raise SystemExit(f"--{name.replace('_', '-')} must be > 0")

  entries = discover_entries(args.inputs)
  if len(entries) < 2:
    raise SystemExit("less than two dump files found")

  output_dir = Path(args.output_dir or f"compare_out_{datetime.now().strftime('%Y%m%d_%H%M%S')}").resolve()
  output_dir.mkdir(parents=True, exist_ok=True)

  groups: dict[str, list[DumpEntry]] = {}
  for entry in entries:
    groups.setdefault(entry.group_key, []).append(entry)

  summary = {
    "created_at": datetime.now().isoformat(timespec="seconds"),
    "inputs": [str(Path(p).expanduser().resolve()) for p in args.inputs],
    "settings": {
      "min_entropy": args.min_entropy,
      "stride": args.stride,
      "window": args.window,
      "window_step": args.window_step,
      "top_stable": args.top_stable,
      "global_top_stable": args.global_top_stable,
      "top_variable": args.top_variable,
      "global_top_variable": args.global_top_variable,
    },
    "groups": {},
  }
  all_stable: list[StableCandidate] = []
  all_variable: list[VariableRegion] = []

  for group_key, group_entries in sorted(groups.items()):
    group_entries = sorted(group_entries, key=lambda e: e.run_label)
    if len(group_entries) < 2:
      summary["groups"][group_key] = {
        "skipped": "only_one_run",
        "entries": [asdict(e) for e in group_entries],
      }
      continue
    datas = [Path(e.dump_path).read_bytes() for e in group_entries]
    min_size = min(len(data) for data in datas)
    if len({len(data) for data in datas}) != 1:
      size_note = f"sizes differ; comparing first {min_size} bytes"
      datas = [data[:min_size] for data in datas]
    else:
      size_note = "sizes match"

    range_start = None
    if group_entries[0].range_start:
      range_start = parse_int(group_entries[0].range_start)
    compare = byte_change_summary(datas)
    compare["size_note"] = size_note

    stable = scan_stable_candidates(
      group_key,
      datas,
      range_start,
      args.min_entropy,
      args.stride,
      args.top_stable,
    )
    variable = scan_variable_regions(
      group_key,
      datas,
      range_start,
      args.window,
      args.window_step,
      args.top_variable,
    )
    all_stable.extend(stable)
    all_variable.extend(variable)
    summary["groups"][group_key] = {
      "entries": [asdict(e) for e in group_entries],
      "compare": compare,
      "stable_candidate_count": len(stable),
      "variable_region_count": len(variable),
    }

  all_stable.sort(key=lambda c: c.score, reverse=True)
  all_stable = all_stable[:args.global_top_stable]
  all_variable.sort(key=lambda r: (r.changed_ratio, r.unique_window_values), reverse=True)
  all_variable = all_variable[:args.global_top_variable]

  summary_json = output_dir / "run_compare_summary.json"
  stable_csv = output_dir / "stable_candidates.csv"
  variable_csv = output_dir / "variable_regions.csv"
  report_md = output_dir / "run_compare_report.md"

  summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  write_csv(stable_csv, all_stable, list(StableCandidate.__dataclass_fields__.keys()))
  write_csv(variable_csv, all_variable, list(VariableRegion.__dataclass_fields__.keys()))
  write_report(report_md, summary, all_stable, all_variable)

  compared_groups = sum(1 for info in summary["groups"].values() if not info.get("skipped"))
  print(f"[INFO] dump files found: {len(entries)}")
  print(f"[INFO] groups compared: {compared_groups}")
  print(f"[INFO] stable candidates written: {len(all_stable)}")
  print(f"[INFO] variable regions written: {len(all_variable)}")
  print(f"[INFO] report: {report_md}")
  print(f"[INFO] stable csv: {stable_csv}")
  print(f"[INFO] variable csv: {variable_csv}")
  print(f"[INFO] summary: {summary_json}")
  print("[INFO] offline comparison complete; no candidate was accepted or written.")


if __name__ == "__main__":
  main()
