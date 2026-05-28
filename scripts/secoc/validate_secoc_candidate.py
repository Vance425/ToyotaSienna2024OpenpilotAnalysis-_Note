#!/usr/bin/env python3
"""
Validate one or more SecOC candidate keys offline.

This tool does not connect to a car and does not write openpilot params. It
checks whether a candidate is well-formed, appears in dump runs, is stable
across runs, and is compatible with the old Toyota SecOC key-table wrapper.
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
OLD_STRUCT_SIZE = 0x20
OLD_KEY_OFFSET = 0x0C
OLD_CHECKSUM_OFFSET = 0x1D
LOG_PATTERNS = {
  "secoc_key_missing": re.compile(r"SecOCKey.*missing|missing.*SecOCKey", re.IGNORECASE),
  "mac_mismatch": re.compile(r"MAC.*mismatch|mismatch.*MAC", re.IGNORECASE),
  "sync_failed": re.compile(r"sync.*fail|fail.*sync", re.IGNORECASE),
  "secoc": re.compile(r"SecOC", re.IGNORECASE),
  "auth": re.compile(r"auth|authenticate|authentication", re.IGNORECASE),
}


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
class CandidateValidation:
  candidate_hex: str
  source: str
  length: int
  entropy: float
  unique_bytes: int
  zero_bytes: int
  ff_bytes: int
  printable_ratio: float
  basic_status: str
  dumps_checked: int
  dumps_with_candidate: int
  stable_positions: str
  expected_position_ok: str
  old_wrapper_hits: int
  old_wrapper_all_expected: bool
  score: float
  verdict: str
  notes: str


def parse_int(text: str) -> int:
  return int(str(text), 0)


def normalize_hex(text: str) -> str:
  cleaned = re.sub(r"[^0-9a-fA-F]", "", text or "")
  if len(cleaned) % 2:
    raise ValueError(f"candidate hex has odd length: {text}")
  return cleaned.lower()


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
  return sum(1 for b in data if 0x20 <= b <= 0x7E) / len(data)


def sha256_bytes(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


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
  return next((part for part in reversed(path.parts) if part), str(path))


def group_key_for(dump_path: Path, range_start: int | None, range_end: int | None) -> str:
  if range_start is not None and range_end is not None:
    return f"{range_start:08x}_{range_end:08x}"
  stem = re.sub(r"^dump_?", "", dump_path.stem)
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


def old_wrapper_hit(data: bytes, offset: int) -> bool:
  if offset < OLD_KEY_OFFSET:
    return False
  struct_start = offset - OLD_KEY_OFFSET
  if struct_start % OLD_STRUCT_SIZE != 0:
    return False
  struct = data[struct_start:struct_start + OLD_STRUCT_SIZE]
  return len(struct) == OLD_STRUCT_SIZE and checksum_hit_for_struct(struct)


def find_all(data: bytes, needle: bytes) -> list[int]:
  hits = []
  pos = data.find(needle)
  while pos >= 0:
    hits.append(pos)
    pos = data.find(needle, pos + 1)
  return hits


def candidate_basic_status(candidate: bytes) -> tuple[str, list[str]]:
  notes = []
  if len(candidate) != DEFAULT_KEY_SIZE:
    notes.append(f"length_{len(candidate)}_not_{DEFAULT_KEY_SIZE}")
  if candidate == b"\x00" * len(candidate):
    notes.append("all_zero")
  if candidate == b"\xff" * len(candidate):
    notes.append("all_ff")
  if len(set(candidate)) <= 2:
    notes.append("low_variation")
  if printable_ratio(candidate) > 0.75:
    notes.append("mostly_ascii")
  if entropy(candidate) >= 3.25 and len(set(candidate)) >= 10:
    notes.append("key_like_entropy")
  status = "ok"
  if any(item in notes for item in ("all_zero", "all_ff", "low_variation")) or len(candidate) != DEFAULT_KEY_SIZE:
    status = "weak"
  return status, notes


def expected_offset_for(entry: DumpEntry, expected_offset: int | None, absolute_address: int | None) -> int | None:
  if expected_offset is not None:
    return expected_offset
  if absolute_address is not None and entry.range_start:
    return absolute_address - parse_int(entry.range_start)
  return None


def validate_candidate(
  candidate_hex: str,
  source: str,
  entries: list[DumpEntry],
  expected_offset: int | None,
  absolute_address: int | None,
  group_key_filter: str | None,
) -> tuple[CandidateValidation, list[dict]]:
  candidate = bytes.fromhex(candidate_hex)
  basic_status, notes = candidate_basic_status(candidate)
  details = []
  positions_by_dump = {}
  expected_results = []
  wrapper_hits = 0

  filtered_entries = [e for e in entries if not group_key_filter or e.group_key == group_key_filter]
  for entry in filtered_entries:
    data = Path(entry.dump_path).read_bytes()
    hits = find_all(data, candidate)
    expected = expected_offset_for(entry, expected_offset, absolute_address)
    expected_ok = None
    if expected is not None:
      expected_ok = 0 <= expected <= len(data) - len(candidate) and data[expected:expected + len(candidate)] == candidate
      expected_results.append(expected_ok)
    wrappers = [pos for pos in hits if old_wrapper_hit(data, pos)]
    wrapper_hits += len(wrappers)
    positions_by_dump[entry.dump_name + "@" + entry.run_label] = hits
    details.append({
      "run_label": entry.run_label,
      "dump_file": entry.dump_name,
      "group_key": entry.group_key,
      "range_start": entry.range_start,
      "range_end": entry.range_end,
      "hits": [f"0x{x:04x}" for x in hits],
      "absolute_hits": [
        f"0x{parse_int(entry.range_start) + x:08x}" for x in hits
      ] if entry.range_start else [],
      "expected_offset": f"0x{expected:04x}" if expected is not None else None,
      "expected_ok": expected_ok,
      "old_wrapper_hits": [f"0x{x:04x}" for x in wrappers],
    })

  dumps_with_candidate = sum(1 for hits in positions_by_dump.values() if hits)
  stable_positions = ""
  if positions_by_dump:
    normalized = [tuple(hits) for hits in positions_by_dump.values()]
    if normalized and len(set(normalized)) == 1:
      stable_positions = ",".join(f"0x{x:04x}" for x in normalized[0])
    else:
      common = set(normalized[0]) if normalized else set()
      for hits in normalized[1:]:
        common &= set(hits)
      stable_positions = ",".join(f"0x{x:04x}" for x in sorted(common))

  expected_position_ok = "not_checked"
  if expected_results:
    if all(expected_results):
      expected_position_ok = "all_ok"
    elif any(expected_results):
      expected_position_ok = "partial"
    else:
      expected_position_ok = "none"

  old_wrapper_all_expected = False
  if expected_offset is not None or absolute_address is not None:
    old_wrapper_all_expected = bool(filtered_entries) and all(
      any(
        hit == expected_offset_for(entry, expected_offset, absolute_address)
        for hit in [int(x, 16) for x in next((d["old_wrapper_hits"] for d in details if d["dump_file"] == entry.dump_name and d["run_label"] == entry.run_label), [])]
      )
      for entry in filtered_entries
    )
  elif stable_positions:
    stable_first = parse_int(stable_positions.split(",")[0])
    old_wrapper_all_expected = bool(filtered_entries) and all(
      old_wrapper_hit(Path(entry.dump_path).read_bytes(), stable_first)
      for entry in filtered_entries
    )

  score = 0.0
  ent = entropy(candidate)
  score += ent * 18.0
  score += min(len(set(candidate)), 16) * 1.5
  if basic_status == "ok":
    score += 15.0
  if filtered_entries:
    score += (dumps_with_candidate / len(filtered_entries)) * 30.0
  if stable_positions:
    score += 20.0
  if expected_position_ok == "all_ok":
    score += 20.0
  if old_wrapper_all_expected:
    score += 35.0
  elif wrapper_hits:
    score += 15.0
  if basic_status == "weak":
    score -= 40.0

  verdict = "reject"
  if basic_status == "ok" and dumps_with_candidate == len(filtered_entries) and stable_positions:
    verdict = "promising"
  if verdict == "promising" and (old_wrapper_all_expected or wrapper_hits >= len(filtered_entries)):
    verdict = "strong_candidate"
  if not filtered_entries:
    verdict = "no_dumps_checked"
  elif dumps_with_candidate == 0:
    verdict = "not_found"

  validation = CandidateValidation(
    candidate_hex=candidate_hex,
    source=source,
    length=len(candidate),
    entropy=round(ent, 4),
    unique_bytes=len(set(candidate)),
    zero_bytes=candidate.count(0),
    ff_bytes=candidate.count(0xFF),
    printable_ratio=round(printable_ratio(candidate), 4),
    basic_status=basic_status,
    dumps_checked=len(filtered_entries),
    dumps_with_candidate=dumps_with_candidate,
    stable_positions=stable_positions,
    expected_position_ok=expected_position_ok,
    old_wrapper_hits=wrapper_hits,
    old_wrapper_all_expected=old_wrapper_all_expected,
    score=round(score, 3),
    verdict=verdict,
    notes=";".join(notes),
  )
  return validation, details


def candidates_from_csv(path: Path, limit: int | None) -> list[tuple[str, str]]:
  candidates = []
  with path.open("r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, 1):
      raw = row.get("candidate_hex") or row.get("candidate") or row.get("hex")
      if not raw:
        continue
      try:
        candidates.append((normalize_hex(raw), f"{path.name}:row{idx}"))
      except ValueError:
        continue
      if limit and len(candidates) >= limit:
        break
  return candidates


def scan_logs(paths: list[str]) -> dict:
  result = {
    "files": [],
    "counts": {name: 0 for name in LOG_PATTERNS},
    "snippets": [],
  }
  files = []
  for raw in paths:
    path = Path(raw).expanduser()
    if path.is_file():
      files.append(path.resolve())
    elif path.is_dir():
      files.extend(sorted(path.rglob("*.log")))
      files.extend(sorted(path.rglob("*.txt")))
  seen = set()
  for path in files:
    if path in seen:
      continue
    seen.add(path)
    file_counts = {name: 0 for name in LOG_PATTERNS}
    try:
      lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as exc:
      result["files"].append({"path": str(path), "error": str(exc)})
      continue
    for lineno, line in enumerate(lines, 1):
      for name, pattern in LOG_PATTERNS.items():
        if pattern.search(line):
          file_counts[name] += 1
          result["counts"][name] += 1
          if len(result["snippets"]) < 80:
            result["snippets"].append({
              "path": str(path),
              "line": lineno,
              "pattern": name,
              "text": line[-240:],
            })
    result["files"].append({"path": str(path), "counts": file_counts})
  return result


def write_csv(path: Path, rows: list[CandidateValidation]) -> None:
  with path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(CandidateValidation.__dataclass_fields__.keys()))
    writer.writeheader()
    for row in rows:
      writer.writerow(asdict(row))


def write_report(path: Path, payload: dict) -> None:
  validations = [CandidateValidation(**item) for item in payload.get("validations", [])]
  lines = [
    "# SecOC Candidate Validation Report",
    "",
    f"Generated: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
    "",
    "This is an offline validation report. It cannot prove that a candidate is a valid Toyota Sienna 2024 SecOC/TSK key.",
    "",
    "## Candidates",
    "",
  ]
  if not validations:
    lines.append("No candidates validated.")
  else:
    lines.append("| rank | verdict | score | candidate | dumps | stable positions | old wrapper | notes |")
    lines.append("|---:|---|---:|---|---:|---|---|---|")
    for idx, item in enumerate(validations, 1):
      lines.append(
        f"| {idx} | `{item.verdict}` | `{item.score}` | `{item.candidate_hex}` | "
        f"`{item.dumps_with_candidate}/{item.dumps_checked}` | `{item.stable_positions}` | "
        f"`{item.old_wrapper_all_expected}` | `{item.notes}` |"
      )
  log_scan = payload.get("log_scan")
  if log_scan:
    lines.extend(["", "## Log Scan", ""])
    lines.append("| pattern | count |")
    lines.append("|---|---:|")
    for name, count in log_scan.get("counts", {}).items():
      lines.append(f"| `{name}` | `{count}` |")
    if log_scan.get("snippets"):
      lines.extend(["", "### Snippets", ""])
      for snippet in log_scan["snippets"][:30]:
        lines.append(f"- `{snippet['pattern']}` {snippet['path']}:{snippet['line']}: `{snippet['text']}`")
  lines.extend([
    "",
    "## Interpretation",
    "",
    "- `strong_candidate`: structurally promising, stable, and old wrapper evidence exists. Still not proof.",
    "- `promising`: well-formed and stable in the provided dumps, but wrapper proof may be missing.",
    "- `not_found`: candidate does not appear in the provided dumps or range.",
    "- `reject`: weak candidate shape, unstable evidence, or insufficient support.",
  ])
  path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Validate Sienna 2024 SecOC candidates offline")
  parser.add_argument("inputs", nargs="*", help="dump run directories or dump .bin files")
  parser.add_argument("--candidate", action="append", help="16-byte candidate hex; can repeat")
  parser.add_argument("--candidate-csv", help="candidate_keys.csv or stable_candidates.csv")
  parser.add_argument("--top", type=int, default=20, help="max rows loaded from --candidate-csv")
  parser.add_argument("--offset", help="expected dump-file offset, e.g. 0x004c")
  parser.add_argument("--absolute-address", help="expected absolute address, e.g. 0xfebe6e80")
  parser.add_argument("--group-key", help="only validate against one dump range group, e.g. febe6e34_febe6ff4")
  parser.add_argument("--openpilot-log", action="append", default=[], help="openpilot log file or directory to scan")
  parser.add_argument("--output-dir", help="output directory; default: validate_out_YYYYMMDD_HHMMSS")
  return parser


def main() -> None:
  args = build_arg_parser().parse_args()
  candidates: list[tuple[str, str]] = []
  for raw in args.candidate or []:
    candidates.append((normalize_hex(raw), "cli"))
  if args.candidate_csv:
    candidates.extend(candidates_from_csv(Path(args.candidate_csv).expanduser(), args.top))
  if not candidates:
    raise SystemExit("provide --candidate HEX or --candidate-csv CSV")

  entries = discover_entries(args.inputs)
  expected_offset = parse_int(args.offset) if args.offset else None
  absolute_address = parse_int(args.absolute_address) if args.absolute_address else None

  output_dir = Path(args.output_dir or f"validate_out_{datetime.now().strftime('%Y%m%d_%H%M%S')}").resolve()
  output_dir.mkdir(parents=True, exist_ok=True)

  validations: list[CandidateValidation] = []
  detail_payload = {}
  for candidate_hex, source in candidates:
    validation, details = validate_candidate(
      candidate_hex,
      source,
      entries,
      expected_offset,
      absolute_address,
      args.group_key,
    )
    validations.append(validation)
    detail_payload[candidate_hex] = details
  validations.sort(key=lambda item: item.score, reverse=True)

  log_scan = scan_logs(args.openpilot_log) if args.openpilot_log else None
  payload = {
    "created_at": datetime.now().isoformat(timespec="seconds"),
    "inputs": [str(Path(p).expanduser().resolve()) for p in args.inputs],
    "settings": {
      "offset": args.offset,
      "absolute_address": args.absolute_address,
      "group_key": args.group_key,
      "candidate_csv": args.candidate_csv,
      "top": args.top,
    },
    "dumps": [asdict(entry) for entry in entries],
    "validations": [asdict(item) for item in validations],
    "details": detail_payload,
    "log_scan": log_scan,
  }

  report_md = output_dir / "candidate_validation_report.md"
  report_json = output_dir / "candidate_validation.json"
  csv_path = output_dir / "candidate_validation.csv"

  report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  write_csv(csv_path, validations)
  write_report(report_md, payload)

  print(f"[INFO] candidates validated: {len(validations)}")
  print(f"[INFO] dumps checked: {len(entries)}")
  print(f"[INFO] report: {report_md}")
  print(f"[INFO] json: {report_json}")
  print(f"[INFO] csv: {csv_path}")
  print("[INFO] offline validation complete; no candidate was written.")


if __name__ == "__main__":
  main()
