#!/usr/bin/env python3
"""
Generic local-window protected-lifecycle triage for selected NDJSON files.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


ADDR_116 = 0x116
ADDR_131 = 0x131
ADDR_260 = 0x260
ADDR_2E4 = 0x2E4

TOP_TIER_ZONE = "fff4"
EXIT_ZONE = "fff0"
CORRIDOR_ZONES = {"fff4", "fff0", "ffee", "ffeb", "ffe8", "ffe7"}


@dataclass
class Frame116:
    ts_ms: int
    phase_hex: str
    phase_sum: int
    family131: Optional[str]
    family260: Optional[str]


@dataclass
class ParsedFile:
    path: Path
    first_ts: int
    last_ts: int
    frames116: list[Frame116]
    e2e_timestamps: list[int]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Window-level protected-lifecycle triage")
    parser.add_argument("inputs", nargs="+", help="NDJSON files to scan")
    parser.add_argument("--window-ms", type=int, default=15000)
    parser.add_argument("--step-ms", type=int, default=5000)
    parser.add_argument(
        "--output-dir",
        default="<LOCAL_ANALYSIS_WORKSPACE>\\analysis-output\\session_window_triage",
    )
    parser.add_argument("--bus", type=int, default=0)
    return parser.parse_args()


def normalize_path_for_runtime(path: Path) -> Path:
    raw = str(path)
    if len(raw) >= 3 and raw[1:3] == ":\\":
        drive = raw[0].lower()
        rest = raw[3:].replace("\\", "/")
        return Path(f"/mnt/{drive}/{rest}")
    return path


def hex16(data: bytes, start: int, end: int) -> str:
    return data[start:end].hex()


def parse_file(path: Path, preferred_bus: int) -> ParsedFile:
    latest_131: tuple[int, str] | None = None
    latest_260: tuple[int, str] | None = None
    frames116: list[Frame116] = []
    e2e_timestamps: list[int] = []
    first_ts: int | None = None
    last_ts: int | None = None

    with normalize_path_for_runtime(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("bus") != preferred_bus:
                continue
            addr = row.get("addr")
            ts_ms = row.get("ts_ms")
            data_hex = row.get("data")
            if not isinstance(addr, int) or not isinstance(ts_ms, int) or not isinstance(data_hex, str):
                continue
            try:
                data = bytes.fromhex(data_hex)
            except ValueError:
                continue

            if first_ts is None:
                first_ts = ts_ms
            last_ts = ts_ms

            if addr == ADDR_131 and len(data) >= 4:
                latest_131 = (ts_ms, hex16(data, 2, 4))
            elif addr == ADDR_260 and len(data) >= 5:
                latest_260 = (ts_ms, hex16(data, 3, 5))
            elif addr == ADDR_116 and len(data) >= 2:
                fam131 = None
                fam260 = None
                if latest_131 and ts_ms - latest_131[0] <= 250:
                    fam131 = latest_131[1]
                if latest_260 and ts_ms - latest_260[0] <= 250:
                    fam260 = latest_260[1]
                frames116.append(
                    Frame116(
                        ts_ms=ts_ms,
                        phase_hex=hex16(data, 0, 2),
                        phase_sum=data[0] + data[1],
                        family131=fam131,
                        family260=fam260,
                    )
                )
            elif addr == ADDR_2E4:
                e2e_timestamps.append(ts_ms)

    if first_ts is None or last_ts is None:
        raise RuntimeError(f"No usable bus-{preferred_bus} data in {path}")

    return ParsedFile(path=path, first_ts=first_ts, last_ts=last_ts, frames116=frames116, e2e_timestamps=e2e_timestamps)


def ladder_level(grade: str, has_seed: bool, has_ramp: bool, has_plateau: bool, has_exit: bool, corridor_ratio: float) -> str:
    if grade == "A":
        return "5"
    if has_seed and has_ramp and has_plateau:
        return "4.5_candidate"
    if has_seed and has_ramp:
        return "3"
    if has_seed and corridor_ratio >= 0.20:
        return "2"
    if has_seed:
        return "1"
    if corridor_ratio >= 0.20:
        return "C_only"
    return ""


def grade_window(frames: list[Frame116]) -> dict[str, object]:
    if not frames:
        return {}

    has_seed = False
    has_ramp = False
    has_plateau = False
    has_exit = False
    corridor_hits = 0
    aligned_hits = 0
    fff4_hits = 0
    max_phase_sum = 0

    for frame in frames:
        fam131 = frame.family131
        fam260 = frame.family260
        max_phase_sum = max(max_phase_sum, frame.phase_sum)
        if fam131 and fam260 and fam131 == fam260:
            aligned_hits += 1
        if fam131 in CORRIDOR_ZONES and fam260 in CORRIDOR_ZONES:
            corridor_hits += 1
        if fam131 == TOP_TIER_ZONE and fam260 == TOP_TIER_ZONE:
            fff4_hits += 1
            if frame.phase_hex == "0000":
                has_seed = True
            if 1 <= frame.phase_sum < 130:
                has_ramp = True
            if frame.phase_sum >= 130:
                has_plateau = True
        if has_plateau and fam131 == TOP_TIER_ZONE and fam260 == EXIT_ZONE:
            has_exit = True

    total = len(frames)
    corridor_ratio = corridor_hits / total if total else 0.0
    aligned_ratio = aligned_hits / total if total else 0.0

    grade = "D"
    if has_seed and has_ramp and has_plateau and has_exit:
        grade = "A"
    elif has_seed:
        grade = "B"
    elif corridor_ratio >= 0.20:
        grade = "C"

    return {
        "frame116_count": total,
        "seed_touch_present": int(has_seed),
        "ramp_present": int(has_ramp),
        "phase_plateau_present": int(has_plateau),
        "phase_exit_present": int(has_exit),
        "corridor_ratio": round(corridor_ratio, 3),
        "aligned_ratio": round(aligned_ratio, 3),
        "fff4_hits": fff4_hits,
        "max_phase_sum": max_phase_sum,
        "grade": grade,
        "ladder_level": ladder_level(grade, has_seed, has_ramp, has_plateau, has_exit, corridor_ratio),
    }


def count_2e4(timestamps: list[int], start: int, end: int) -> int:
    return sum(1 for ts in timestamps if start <= ts < end)


def scan_windows(parsed: ParsedFile, window_ms: int, step_ms: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    start = parsed.first_ts
    while start + window_ms <= parsed.last_ts:
        end = start + window_ms
        frames = [f for f in parsed.frames116 if start <= f.ts_ms < end]
        scored = grade_window(frames)
        if scored:
            rows.append(
                {
                    "sample_id": parsed.path.stem,
                    "source_path": str(parsed.path),
                    "window_start_ts": start,
                    "window_end_ts": end,
                    "window_rel_start_s": round((start - parsed.first_ts) / 1000.0, 3),
                    "window_rel_end_s": round((end - parsed.first_ts) / 1000.0, 3),
                    "count_2e4": count_2e4(parsed.e2e_timestamps, start, end),
                    **scored,
                }
            )
        start += step_ms
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    parsed = [parse_file(Path(p), args.bus) for p in args.inputs]
    all_rows: list[dict[str, object]] = []
    for item in parsed:
        all_rows.extend(scan_windows(item, args.window_ms, args.step_ms))

    rank = {"5": 5, "4.5_candidate": 4, "3": 3, "2": 2, "1": 1, "C_only": 0, "": -1}
    shortlist = [r for r in all_rows if r["grade"] in {"A", "B"}]
    shortlist.sort(
        key=lambda r: (
            rank.get(str(r["ladder_level"]), -1),
            int(r["phase_plateau_present"]),
            int(r["phase_exit_present"]),
            int(r["ramp_present"]),
            float(r["corridor_ratio"]),
            int(r["max_phase_sum"]),
            int(r["count_2e4"]),
        ),
        reverse=True,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "window_summary.csv", all_rows)
    write_csv(out_dir / "shortlist.csv", shortlist)
    (out_dir / "manifest.json").write_text(
        json.dumps(
            {
                "inputs": args.inputs,
                "window_ms": args.window_ms,
                "step_ms": args.step_ms,
                "bus": args.bus,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"window_summary": str(out_dir / "window_summary.csv"), "shortlist": str(out_dir / "shortlist.csv")}, indent=2))


if __name__ == "__main__":
    main()
