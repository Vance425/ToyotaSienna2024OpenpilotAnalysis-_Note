#!/usr/bin/env python3
"""
Window-level triage for bridge-gap candidate files.

Scans selected 4.5-candidate files with 15-second windows and 5-second stride,
then scores each window using the current protected-lifecycle heuristic.
"""

from __future__ import annotations

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

WINDOW_MS = 15000
STEP_MS = 5000
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "analysis-output" / "bridge_gap_window_triage"


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
    count2e4_by_ts: list[int]


def normalize_path_for_runtime(path: Path) -> Path:
    raw = str(path)
    if len(raw) >= 3 and raw[1:3] == ":\\":
        drive = raw[0].lower()
        rest = raw[3:].replace("\\", "/")
        return Path(f"/mnt/{drive}/{rest}")
    return path


def hex16(data: bytes, start: int, end: int) -> str:
    return data[start:end].hex()


def parse_file(path: Path, preferred_bus: int = 0) -> ParsedFile:
    path = normalize_path_for_runtime(path)
    latest_131: tuple[int, str] | None = None
    latest_260: tuple[int, str] | None = None
    frames116: list[Frame116] = []
    e2e_timestamps: list[int] = []
    first_ts: int | None = None
    last_ts: int | None = None

    with path.open("r", encoding="utf-8") as handle:
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
        raise RuntimeError(f"no usable bus=0 frames in {path}")

    return ParsedFile(
        path=path,
        first_ts=first_ts,
        last_ts=last_ts,
        frames116=frames116,
        count2e4_by_ts=e2e_timestamps,
    )


def window_count(values: list[int], start_ts: int, end_ts: int) -> int:
    return sum(1 for ts in values if start_ts <= ts < end_ts)


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


def analyze_candidate(path: Path) -> list[dict[str, object]]:
    parsed = parse_file(path)
    rows: list[dict[str, object]] = []
    start = parsed.first_ts
    end_limit = parsed.last_ts
    while start + WINDOW_MS <= end_limit:
        end = start + WINDOW_MS
        frames = [f for f in parsed.frames116 if start <= f.ts_ms < end]
        scored = grade_window(frames)
        if scored:
            rows.append(
                {
                    "sample_id": path.stem,
                    "source_path": str(path),
                    "window_start_ts": start,
                    "window_end_ts": end,
                    "window_rel_start_s": round((start - parsed.first_ts) / 1000.0, 3),
                    "window_rel_end_s": round((end - parsed.first_ts) / 1000.0, 3),
                    "count_2e4": window_count(parsed.count2e4_by_ts, start, end),
                    **scored,
                }
            )
        start += STEP_MS
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run() -> None:
    candidates = [
        Path(r"<LOCAL_RAW_CAN_LOG>\20260426\raw_can_logs\toyota_all_20260426_045606_007.ndjson"),
        Path(r"<LOCAL_RAW_CAN_LOG>\20260426\raw_can_logs\toyota_seg_IGN_ON_20260426_045640_014.ndjson"),
        Path(r"<LOCAL_RAW_CAN_LOG>\20260426\raw_can_logs\toyota_all_20260426_051051_010.ndjson"),
        Path(r"<LOCAL_RAW_CAN_LOG>\20260426\raw_can_logs\toyota_seg_IGN_ON_20260426_051136_020.ndjson"),
    ]
    all_rows: list[dict[str, object]] = []
    for path in candidates:
        all_rows.extend(analyze_candidate(path))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "window_summary.csv", all_rows)
    shortlist = [
        row for row in all_rows
        if row["grade"] in {"A", "B"}
    ]
    # Sort strongest-first by ladder/plateau/ramp/corridor/phase.
    rank = {"5": 5, "4.5_candidate": 4, "3": 3, "2": 2, "1": 1, "C_only": 0, "": -1}
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
    write_csv(OUTPUT_DIR / "shortlist.csv", shortlist)
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(
            {
                "window_ms": WINDOW_MS,
                "step_ms": STEP_MS,
                "candidates": [str(p) for p in candidates],
                "output_dir": str(OUTPUT_DIR),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"window_summary": str(OUTPUT_DIR / "window_summary.csv"), "shortlist": str(OUTPUT_DIR / "shortlist.csv")}, indent=2))


if __name__ == "__main__":
    run()
