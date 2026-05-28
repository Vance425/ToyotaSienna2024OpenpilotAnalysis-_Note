#!/usr/bin/env python3
import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


ADDR_116 = 0x116
ADDR_131 = 0x131
ADDR_260 = 0x260

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
    raw_data: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Heuristic grader for Toyota Sienna passive CAN logs."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="One or more .ndjson files or directories containing .ndjson files.",
    )
    parser.add_argument(
        "--output-dir",
        default="<LOCAL_ANALYSIS_WORKSPACE>\\analysis-output",
        help="Directory for CSV/JSON output.",
    )
    parser.add_argument(
        "--bus",
        type=int,
        default=0,
        help="Preferred CAN bus to analyze. Default: 0",
    )
    return parser.parse_args()


def iter_ndjson_files(inputs: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_file() and path.suffix.lower() == ".ndjson":
            files.append(path)
            continue
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*.ndjson") if p.is_file()))
    seen: set[Path] = set()
    unique_files: list[Path] = []
    for file in files:
        if file not in seen:
            unique_files.append(file)
            seen.add(file)
    return unique_files


def hex16(data: bytes, start: int, end: int) -> str:
    return data[start:end].hex()


def analyze_file(path: Path, preferred_bus: int) -> dict:
    latest_131: tuple[int, str] | None = None
    latest_260: tuple[int, str] | None = None
    frames_116: list[Frame116] = []

    bus_counts: dict[int, int] = {}
    parse_errors = 0

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if f'"bus":{preferred_bus}' not in line:
                continue
            if (
                f'"addr":{ADDR_116}' not in line
                and f'"addr":{ADDR_131}' not in line
                and f'"addr":{ADDR_260}' not in line
            ):
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue

            bus = row.get("bus")
            addr = row.get("addr")
            ts_ms = row.get("ts_ms")
            data_hex = row.get("data")
            if not isinstance(bus, int) or not isinstance(addr, int):
                continue
            if not isinstance(ts_ms, int) or not isinstance(data_hex, str):
                continue

            bus_counts[bus] = bus_counts.get(bus, 0) + 1
            try:
                data = bytes.fromhex(data_hex)
            except ValueError:
                parse_errors += 1
                continue

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
                frames_116.append(
                    Frame116(
                        ts_ms=ts_ms,
                        phase_hex=hex16(data, 0, 2),
                        phase_sum=data[0] + data[1],
                        family131=fam131,
                        family260=fam260,
                        raw_data=data_hex,
                    )
                )

    has_seed = False
    has_ramp = False
    has_plateau = False
    has_exit = False
    has_corridor = False
    top_tier_peaks: list[Frame116] = []
    positive_high_phase_peaks: list[Frame116] = []
    seed_ts: Optional[int] = None
    plateau_ts: Optional[int] = None

    for frame in frames_116:
        if frame.family131 in CORRIDOR_ZONES and frame.family260 in CORRIDOR_ZONES:
            has_corridor = True
        if frame.family131 == TOP_TIER_ZONE and frame.family260 == TOP_TIER_ZONE:
            if frame.phase_hex == "0000":
                has_seed = True
                if seed_ts is None:
                    seed_ts = frame.ts_ms
            if frame.phase_sum >= 130:
                has_plateau = True
                plateau_ts = frame.ts_ms if plateau_ts is None else plateau_ts
                top_tier_peaks.append(frame)
            if 1 <= frame.phase_sum < 130:
                has_ramp = True
        elif frame.phase_sum >= 130 and (
            frame.family131 not in CORRIDOR_ZONES or frame.family260 not in CORRIDOR_ZONES
        ):
            positive_high_phase_peaks.append(frame)

        if (
            plateau_ts is not None
            and frame.ts_ms >= plateau_ts
            and frame.family131 == TOP_TIER_ZONE
            and frame.family260 == EXIT_ZONE
        ):
            has_exit = True

    grade = "D"
    reason = "no seed/corridor pattern"
    if has_seed and has_ramp and has_plateau and has_exit:
        grade = "A"
        reason = "seed + ramp + plateau + exit under fff4/fff0 pattern"
    elif has_seed:
        grade = "B"
        reason = "touches fff4|fff4 + 0000 but lacks full lifecycle"
    elif has_corridor:
        grade = "C"
        reason = "corridor activity without full seed state"

    return {
        "file": str(path),
        "bus": preferred_bus,
        "parse_errors": parse_errors,
        "bus_counts": bus_counts,
        "frame116_count": len(frames_116),
        "grade": grade,
        "reason": reason,
        "has_seed": has_seed,
        "has_ramp": has_ramp,
        "has_plateau": has_plateau,
        "has_exit": has_exit,
        "has_corridor": has_corridor,
        "seed_ts": seed_ts,
        "plateau_ts": plateau_ts,
        "top_tier_peak_count": len(top_tier_peaks),
        "top_tier_peak_examples": [
            {
                "ts_ms": frame.ts_ms,
                "phase_hex": frame.phase_hex,
                "phase_sum": frame.phase_sum,
                "family131": frame.family131,
                "family260": frame.family260,
            }
            for frame in top_tier_peaks[:5]
        ],
        "positive_high_phase_examples": [
            {
                "ts_ms": frame.ts_ms,
                "phase_hex": frame.phase_hex,
                "phase_sum": frame.phase_sum,
                "family131": frame.family131,
                "family260": frame.family260,
            }
            for frame in positive_high_phase_peaks[:5]
        ],
    }


def write_outputs(results: list[dict], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "can_log_grades.csv"
    json_path = output_dir / "can_log_grades.json"

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "file",
                "grade",
                "reason",
                "has_seed",
                "has_ramp",
                "has_plateau",
                "has_exit",
                "has_corridor",
                "seed_ts",
                "plateau_ts",
                "top_tier_peak_count",
                "frame116_count",
            ]
        )
        for row in results:
            writer.writerow(
                [
                    row["file"],
                    row["grade"],
                    row["reason"],
                    row["has_seed"],
                    row["has_ramp"],
                    row["has_plateau"],
                    row["has_exit"],
                    row["has_corridor"],
                    row["seed_ts"],
                    row["plateau_ts"],
                    row["top_tier_peak_count"],
                    row["frame116_count"],
                ]
            )

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)

    return csv_path, json_path


def main() -> int:
    args = parse_args()
    files = iter_ndjson_files(args.inputs)
    if not files:
        raise SystemExit("No .ndjson files found.")

    output_dir = Path(args.output_dir)
    results = [analyze_file(path, args.bus) for path in files]
    csv_path, json_path = write_outputs(results, output_dir)

    for row in results:
        print(f"{row['grade']}  {row['file']}  {row['reason']}")

    print(f"\nCSV:  {csv_path}")
    print(f"JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
