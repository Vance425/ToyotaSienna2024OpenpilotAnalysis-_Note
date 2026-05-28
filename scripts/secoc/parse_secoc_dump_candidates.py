#!/usr/bin/env python3
"""
Offline SecOC dump candidate parser.

This tool does not connect to a car and does not write openpilot params. It
only scans raw dump files for key-like byte ranges and layout hints.
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


DEFAULT_STRUCT_SIZES = (0x20, 0x30, 0x40)
DEFAULT_KEY_SIZE = 16
OLD_KEY_OFFSET = 0x0C
OLD_CHECKSUM_OFFSET = 0x1D
MARKERS = {
  "zero16": bytes(16),
  "zero4": bytes.fromhex("00000000"),
  "ff4": bytes.fromhex("ffffffff"),
  "5a5a": bytes.fromhex("5a5a"),
  "2222": bytes.fromhex("2222"),
  "01000000": bytes.fromhex("01000000"),
  "aaaaaaaa": bytes.fromhex("aaaaaaaa"),
  "55555555": bytes.fromhex("55555555"),
}


@dataclass
class DumpFile:
  path: str
  name: str
  size: int
  sha256: str
  range_start: str | None
  range_end: str | None
  metadata_path: str | None


@dataclass
class Candidate:
  dump_file: str
  offset: str
  absolute_address: str | None
  candidate_hex: str
  entropy: float
  unique_bytes: int
  zero_bytes: int
  ff_bytes: int
  ascii_printable_ratio: float
  near_marker: str
  old_checksum_ok: bool
  checksum_hits: str
  struct_size_guess: str
  score: float
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


def printable_ratio(data: bytes) -> float:
  if not data:
    return 0.0
  printable = sum(1 for b in data if 0x20 <= b <= 0x7E)
  return printable / len(data)


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


def discover_dump_files(inputs: list[str]) -> list[Path]:
  found: list[Path] = []
  for raw in inputs:
    path = Path(raw).expanduser()
    if path.is_file():
      if path.suffix.lower() == ".bin":
        found.append(path.resolve())
      continue
    if path.is_dir():
      found.extend(sorted(p.resolve() for p in path.rglob("dump*.bin")))
  seen = set()
  unique = []
  for path in found:
    if path not in seen:
      seen.add(path)
      unique.append(path)
  return unique


def marker_distance(data: bytes, offset: int, radius: int) -> str:
  hits = []
  start = max(0, offset - radius)
  end = min(len(data), offset + DEFAULT_KEY_SIZE + radius)
  region = data[start:end]
  for name, marker in MARKERS.items():
    pos = region.find(marker)
    while pos >= 0:
      marker_at = start + pos
      distance = marker_at - offset
      hits.append(f"{name}@{distance:+d}")
      pos = region.find(marker, pos + 1)
  return ";".join(hits[:8])


def checksum_hit_for_struct(struct: bytes, checksum_offset: int) -> bool:
  if checksum_offset >= len(struct):
    return False
  checksum = (~sum(struct[:checksum_offset])) & 0xFF
  return checksum == struct[checksum_offset]


def checksum_hits(data: bytes, candidate_offset: int, struct_sizes: tuple[int, ...]) -> list[str]:
  hits = []
  for struct_size in struct_sizes:
    starts = set()
    starts.add((candidate_offset // struct_size) * struct_size)
    if candidate_offset >= OLD_KEY_OFFSET:
      starts.add(candidate_offset - OLD_KEY_OFFSET)
    for struct_start in sorted(starts):
      if struct_start < 0 or struct_start + struct_size > len(data):
        continue
      struct = data[struct_start:struct_start + struct_size]
      if checksum_hit_for_struct(struct, OLD_CHECKSUM_OFFSET):
        label = f"struct=0x{struct_size:x},start=0x{struct_start:x},old_off=0x{OLD_CHECKSUM_OFFSET:x}"
        if candidate_offset == struct_start + OLD_KEY_OFFSET:
          label += ",old_key_offset"
        hits.append(label)
      for checksum_offset in range(1, struct_size):
        if checksum_offset == OLD_CHECKSUM_OFFSET:
          continue
        if checksum_hit_for_struct(struct, checksum_offset):
          hits.append(f"struct=0x{struct_size:x},start=0x{struct_start:x},off=0x{checksum_offset:x}")
          break
  return hits


def classify_candidate(chunk: bytes) -> list[str]:
  notes = []
  if chunk == b"\x00" * len(chunk):
    notes.append("all_zero")
  if chunk == b"\xff" * len(chunk):
    notes.append("all_ff")
  if len(set(chunk)) <= 2:
    notes.append("low_variation")
  if printable_ratio(chunk) > 0.75:
    notes.append("mostly_ascii")
  if entropy(chunk) >= 3.25 and len(set(chunk)) >= 10:
    notes.append("key_like_entropy")
  return notes


def score_candidate(chunk: bytes, offset: int, hits: list[str], near_marker: str, aligned16: bool) -> float:
  ent = entropy(chunk)
  unique = len(set(chunk))
  zero = chunk.count(0)
  ff = chunk.count(0xFF)
  score = 0.0
  score += ent * 18.0
  score += min(unique, 16) * 1.5
  if aligned16:
    score += 8.0
  if hits:
    score += 20.0
    if any("old_key_offset" in hit for hit in hits):
      score += 18.0
  if near_marker:
    score += 4.0
  if zero >= 8 or ff >= 8:
    score -= 35.0
  if len(set(chunk)) <= 2:
    score -= 30.0
  if printable_ratio(chunk) > 0.75:
    score -= 10.0
  if offset % 4 == 0:
    score += 2.0
  return round(score, 3)


def scan_candidates(
  dump: DumpFile,
  data: bytes,
  range_start: int | None,
  min_entropy: float,
  top: int,
  stride: int,
  marker_radius: int,
  struct_sizes: tuple[int, ...],
) -> list[Candidate]:
  candidates = []
  for offset in range(0, max(0, len(data) - DEFAULT_KEY_SIZE + 1), stride):
    chunk = data[offset:offset + DEFAULT_KEY_SIZE]
    notes = classify_candidate(chunk)
    if "all_zero" in notes or "all_ff" in notes:
      continue
    ent = entropy(chunk)
    hits = checksum_hits(data, offset, struct_sizes)
    near = marker_distance(data, offset, marker_radius)
    if ent < min_entropy and not hits and not near:
      continue
    score = score_candidate(chunk, offset, hits, near, offset % 16 == 0)
    struct_guess = ";".join(sorted({hit.split(",")[0].split("=")[1] for hit in hits if hit.startswith("struct=")}))
    absolute = f"0x{range_start + offset:08x}" if range_start is not None else None
    candidates.append(Candidate(
      dump_file=dump.name,
      offset=f"0x{offset:04x}",
      absolute_address=absolute,
      candidate_hex=chunk.hex(),
      entropy=round(ent, 4),
      unique_bytes=len(set(chunk)),
      zero_bytes=chunk.count(0),
      ff_bytes=chunk.count(0xFF),
      ascii_printable_ratio=round(printable_ratio(chunk), 4),
      near_marker=near,
      old_checksum_ok=any("old_off=0x1d" in hit for hit in hits),
      checksum_hits=";".join(hits[:10]),
      struct_size_guess=struct_guess,
      score=score,
      notes=";".join(notes),
    ))
  candidates.sort(key=lambda c: c.score, reverse=True)
  return candidates[:top]


def scan_layouts(data: bytes, struct_sizes: tuple[int, ...]) -> list[dict]:
  layouts = []
  for struct_size in struct_sizes:
    total = 0
    old_checksum_hits = []
    any_checksum_hits = []
    old_key_candidates = []
    for start in range(0, max(0, len(data) - struct_size + 1), struct_size):
      struct = data[start:start + struct_size]
      total += 1
      if checksum_hit_for_struct(struct, OLD_CHECKSUM_OFFSET):
        old_checksum_hits.append(start)
      for checksum_offset in range(1, struct_size):
        if checksum_hit_for_struct(struct, checksum_offset):
          any_checksum_hits.append({"struct_start": start, "checksum_offset": checksum_offset})
          break
      key = struct[OLD_KEY_OFFSET:OLD_KEY_OFFSET + DEFAULT_KEY_SIZE]
      if len(key) == DEFAULT_KEY_SIZE and key not in (b"\x00" * 16, b"\xff" * 16):
        old_key_candidates.append({
          "struct_start": f"0x{start:04x}",
          "key_offset": f"0x{start + OLD_KEY_OFFSET:04x}",
          "candidate_hex": key.hex(),
          "entropy": round(entropy(key), 4),
          "old_checksum_ok": start in old_checksum_hits,
        })
    layouts.append({
      "struct_size": f"0x{struct_size:x}",
      "struct_count": total,
      "old_checksum_offset": f"0x{OLD_CHECKSUM_OFFSET:x}",
      "old_checksum_hit_count": len(old_checksum_hits),
      "old_checksum_hits": [f"0x{x:04x}" for x in old_checksum_hits[:32]],
      "any_checksum_hit_count": len(any_checksum_hits),
      "any_checksum_hits": [
        {
          "struct_start": f"0x{item['struct_start']:04x}",
          "checksum_offset": f"0x{item['checksum_offset']:02x}",
        }
        for item in any_checksum_hits[:32]
      ],
      "old_key_offset": f"0x{OLD_KEY_OFFSET:x}",
      "old_key_candidates": old_key_candidates[:32],
    })
  return layouts


def summarize_regions(data: bytes, window: int, step: int) -> list[dict]:
  regions = []
  for start in range(0, max(0, len(data) - window + 1), step):
    chunk = data[start:start + window]
    if chunk == b"\x00" * len(chunk) or chunk == b"\xff" * len(chunk):
      continue
    regions.append({
      "offset": f"0x{start:04x}",
      "size": window,
      "entropy": round(entropy(chunk), 4),
      "unique_bytes": len(set(chunk)),
      "zero_ratio": round(chunk.count(0) / len(chunk), 4),
      "ff_ratio": round(chunk.count(0xFF) / len(chunk), 4),
      "sha256_16": sha256_bytes(chunk)[:16],
    })
  regions.sort(key=lambda r: (r["entropy"], r["unique_bytes"]), reverse=True)
  return regions[:32]


def write_csv(path: Path, candidates: list[Candidate]) -> None:
  fieldnames = list(asdict(candidates[0]).keys()) if candidates else [field.name for field in Candidate.__dataclass_fields__.values()]
  with path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for candidate in candidates:
      writer.writerow(asdict(candidate))


def write_report(path: Path, dumps: list[DumpFile], candidates: list[Candidate], hypotheses: dict) -> None:
  lines = [
    "# SecOC Dump Candidate Report",
    "",
    f"Generated: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
    "",
    "This is an offline candidate scan. A candidate is not proof of a valid Toyota Sienna 2024 SecOC/TSK key.",
    "",
    "## Dumps",
    "",
  ]
  for dump in dumps:
    lines.append(f"- `{dump.name}`")
    lines.append(f"  - size: `{dump.size}`")
    lines.append(f"  - sha256: `{dump.sha256}`")
    if dump.range_start or dump.range_end:
      lines.append(f"  - range: `{dump.range_start} -> {dump.range_end}`")
    if dump.metadata_path:
      lines.append(f"  - metadata: `{dump.metadata_path}`")
  lines.extend(["", "## Top Candidates", ""])
  if not candidates:
    lines.append("No candidates matched the current thresholds.")
  else:
    lines.append("| rank | dump | offset | absolute | score | entropy | old checksum | candidate | notes |")
    lines.append("|---:|---|---:|---:|---:|---:|---|---|---|")
    for idx, candidate in enumerate(candidates[:40], 1):
      lines.append(
        f"| {idx} | `{candidate.dump_file}` | `{candidate.offset}` | `{candidate.absolute_address or ''}` | "
        f"`{candidate.score}` | `{candidate.entropy}` | `{candidate.old_checksum_ok}` | "
        f"`{candidate.candidate_hex}` | `{candidate.notes}` |"
      )
  lines.extend(["", "## Layout Hints", ""])
  for dump_name, info in hypotheses.get("dumps", {}).items():
    lines.append(f"### `{dump_name}`")
    for layout in info.get("layouts", []):
      lines.append(
        f"- struct `{layout['struct_size']}`: old checksum hits `{layout['old_checksum_hit_count']}`, "
        f"any checksum hits `{layout['any_checksum_hit_count']}`"
      )
    lines.append("")
  path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Offline parser for Sienna 2024 SecOC dump candidates")
  parser.add_argument("inputs", nargs="+", help="dump .bin files or directories containing dump*.bin")
  parser.add_argument("--output-dir", help="output directory; default: parse_out_YYYYMMDD_HHMMSS")
  parser.add_argument("--min-entropy", type=float, default=2.75, help="minimum entropy for 16-byte candidates without other hints")
  parser.add_argument("--top", type=int, default=80, help="max candidates per dump before global top sort")
  parser.add_argument("--global-top", type=int, default=200, help="max candidates written globally")
  parser.add_argument("--stride", type=int, default=4, help="candidate scan stride in bytes")
  parser.add_argument("--marker-radius", type=int, default=32, help="bytes around candidate to search for fixed markers")
  parser.add_argument("--struct-size", action="append", help="struct size to scan, e.g. 0x20; can repeat")
  parser.add_argument("--window", type=int, default=64, help="window size for high-entropy region summary")
  parser.add_argument("--window-step", type=int, default=16, help="step for high-entropy region summary")
  return parser


def main() -> None:
  args = build_arg_parser().parse_args()
  struct_sizes = tuple(parse_int(x) for x in args.struct_size) if args.struct_size else DEFAULT_STRUCT_SIZES
  if args.stride <= 0:
    raise SystemExit("--stride must be > 0")
  if args.top <= 0 or args.global_top <= 0:
    raise SystemExit("--top and --global-top must be > 0")

  dump_paths = discover_dump_files(args.inputs)
  if not dump_paths:
    raise SystemExit("no dump*.bin files found")

  output_dir = Path(args.output_dir or f"parse_out_{datetime.now().strftime('%Y%m%d_%H%M%S')}").resolve()
  output_dir.mkdir(parents=True, exist_ok=True)

  dumps: list[DumpFile] = []
  all_candidates: list[Candidate] = []
  hypotheses = {
    "created_at": datetime.now().isoformat(timespec="seconds"),
    "inputs": [str(Path(p).resolve()) for p in args.inputs],
    "settings": {
      "min_entropy": args.min_entropy,
      "top": args.top,
      "global_top": args.global_top,
      "stride": args.stride,
      "marker_radius": args.marker_radius,
      "struct_sizes": [f"0x{x:x}" for x in struct_sizes],
      "window": args.window,
      "window_step": args.window_step,
    },
    "dumps": {},
  }

  for dump_path in dump_paths:
    data = dump_path.read_bytes()
    metadata_path = find_metadata_near(dump_path)
    metadata = load_metadata(metadata_path)
    range_start, range_end = range_from_metadata(dump_path, metadata)
    dump = DumpFile(
      path=str(dump_path),
      name=dump_path.name,
      size=len(data),
      sha256=sha256_bytes(data),
      range_start=f"0x{range_start:08x}" if range_start is not None else None,
      range_end=f"0x{range_end:08x}" if range_end is not None else None,
      metadata_path=str(metadata_path) if metadata_path else None,
    )
    dumps.append(dump)
    candidates = scan_candidates(
      dump,
      data,
      range_start,
      args.min_entropy,
      args.top,
      args.stride,
      args.marker_radius,
      struct_sizes,
    )
    all_candidates.extend(candidates)
    hypotheses["dumps"][dump.name] = {
      "dump": asdict(dump),
      "byte_summary": {
        "size": len(data),
        "entropy": round(entropy(data), 4),
        "unique_bytes": len(set(data)),
        "zero_ratio": round(data.count(0) / len(data), 4) if data else 0,
        "ff_ratio": round(data.count(0xFF) / len(data), 4) if data else 0,
      },
      "layouts": scan_layouts(data, struct_sizes),
      "high_entropy_regions": summarize_regions(data, args.window, args.window_step),
    }

  all_candidates.sort(key=lambda c: c.score, reverse=True)
  all_candidates = all_candidates[:args.global_top]

  candidates_csv = output_dir / "candidate_keys.csv"
  hypotheses_json = output_dir / "layout_hypotheses.json"
  report_md = output_dir / "candidate_report.md"

  write_csv(candidates_csv, all_candidates)
  hypotheses_json.write_text(json.dumps(hypotheses, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  write_report(report_md, dumps, all_candidates, hypotheses)

  print(f"[INFO] dumps parsed: {len(dumps)}")
  print(f"[INFO] candidates written: {len(all_candidates)}")
  print(f"[INFO] report: {report_md}")
  print(f"[INFO] csv: {candidates_csv}")
  print(f"[INFO] layout hypotheses: {hypotheses_json}")
  print("[INFO] offline parser complete; no key was accepted or written.")


if __name__ == "__main__":
  main()
