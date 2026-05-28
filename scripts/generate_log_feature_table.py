#!/usr/bin/env python3
import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


ADDR_116 = 0x116
ADDR_131 = 0x131
ADDR_191 = 0x191
ADDR_260 = 0x260
ADDR_2E4 = 0x2E4
ADDR_D8 = 0x0D8

TOP_TIER_ZONE = "fff4"
EXIT_ZONE = "fff0"
CORRIDOR_ZONES = {"fff4", "fff0", "ffee", "ffeb", "ffe8", "ffe7"}


@dataclass
class Frame116:
    ts_ms: int
    phase_sum: int
    phase_hex: str
    family131: Optional[str]
    family260: Optional[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate cross-log feature tables for Toyota Sienna passive CAN samples."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="One or more .ndjson files or directories containing .ndjson files.",
    )
    parser.add_argument(
        "--output-dir",
        default="<LOCAL_ANALYSIS_WORKSPACE>\\analysis-output",
        help="Output directory for generated CSV/JSON files.",
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


def parse_hex(data: str) -> list[int]:
    return [int(data[i : i + 2], 16) for i in range(0, len(data), 2)]


def s16le(buf: list[int], idx: int) -> int:
    v = buf[idx] | (buf[idx + 1] << 8)
    return v - 65536 if v & 0x8000 else v


def s16be(buf: list[int], idx: int) -> int:
    v = (buf[idx] << 8) | buf[idx + 1]
    return v - 65536 if v & 0x8000 else v


def s8(v: int) -> int:
    return v - 256 if v >= 128 else v


def corr(xs: list[float], ys: list[float]) -> Optional[float]:
    n = min(len(xs), len(ys))
    if n < 5:
        return None
    mx = sum(xs[:n]) / n
    my = sum(ys[:n]) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs[:n], ys[:n]))
    dx = sum((x - mx) ** 2 for x in xs[:n])
    dy = sum((y - my) ** 2 for y in ys[:n])
    if dx == 0 or dy == 0:
        return None
    return num / math.sqrt(dx * dy)


def control_from_260(buf: list[int]) -> int:
    fine = s16le(buf, 2)
    control = fine + (s8(buf[5]) << 8)
    if buf[1] == 0xFF:
        control = -control
    return control


def zone_bucket(hex16_value: Optional[str]) -> str:
    if not hex16_value:
        return ""
    return hex16_value


def ordinal_from_ratio(ratio: float) -> int:
    if ratio <= 0.0:
        return 0
    if ratio < 0.10:
        return 1
    if ratio < 0.35:
        return 2
    return 3


def joined_lifecycle_strength(has_seed: bool, has_ramp: bool, has_plateau: bool, has_exit: bool) -> int:
    if has_seed and has_ramp and has_plateau and has_exit:
        return 3
    if has_seed and has_ramp and has_plateau:
        return 2
    if has_seed and has_ramp:
        return 1
    return 0


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


def classify_value_type(
    grade: str,
    has_seed: bool,
    has_ramp: bool,
    has_plateau: bool,
    companion_mode: str,
    abs_b45: Optional[float],
    abs_b67: Optional[float],
) -> str:
    if grade == "A":
        return "full_event"
    if has_seed or has_ramp or has_plateau:
        return "entry_side"
    best = max(abs_b45 or 0.0, abs_b67 or 0.0)
    if best >= 0.20 or companion_mode in {"b4-b5", "b6-b7", "dual"}:
        return "companion_control"
    return "low_signal"


def analyze_file(path: Path, preferred_bus: int) -> dict:
    latest_131: Optional[tuple[int, str]] = None
    latest_260: Optional[tuple[int, str]] = None
    last_191: Optional[tuple[int, int, int]] = None

    frames_116: list[Frame116] = []
    control_vals: list[float] = []
    comp_b45: list[float] = []
    comp_b67: list[float] = []

    count_2e4 = 0
    count_d8 = 0
    total_bus0_rows = 0
    parse_errors = 0
    first_ts: Optional[int] = None
    last_ts: Optional[int] = None

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue

            bus = row.get("bus")
            if bus != preferred_bus:
                continue
            total_bus0_rows += 1

            addr = row.get("addr")
            ts_ms = row.get("ts_ms")
            data_hex = row.get("data")
            if not isinstance(addr, int) or not isinstance(ts_ms, int) or not isinstance(data_hex, str):
                continue

            if first_ts is None:
                first_ts = ts_ms
            last_ts = ts_ms

            try:
                data = bytes.fromhex(data_hex)
                buf = parse_hex(data_hex)
            except ValueError:
                parse_errors += 1
                continue

            if addr == ADDR_131 and len(data) >= 4:
                latest_131 = (ts_ms, hex16(data, 2, 4))
            elif addr == ADDR_260 and len(data) >= 5:
                latest_260 = (ts_ms, hex16(data, 3, 5))
                if last_191 is not None and abs(ts_ms - last_191[0]) <= 100 and len(buf) >= 8:
                    control_vals.append(float(control_from_260(buf)))
                    comp_b45.append(float(last_191[1]))
                    comp_b67.append(float(last_191[2]))
            elif addr == ADDR_116 and len(data) >= 2:
                fam131 = latest_131[1] if latest_131 and ts_ms - latest_131[0] <= 250 else None
                fam260 = latest_260[1] if latest_260 and ts_ms - latest_260[0] <= 250 else None
                frames_116.append(
                    Frame116(
                        ts_ms=ts_ms,
                        phase_sum=data[0] + data[1],
                        phase_hex=hex16(data, 0, 2),
                        family131=fam131,
                        family260=fam260,
                    )
                )
            elif addr == ADDR_191 and len(buf) >= 8:
                last_191 = (ts_ms, s16le(buf, 4), s16be(buf, 6))
            elif addr == ADDR_2E4:
                count_2e4 += 1
            elif addr == ADDR_D8:
                count_d8 += 1

    has_seed = False
    has_ramp = False
    has_plateau = False
    has_exit = False
    top_tier_peak_count = 0
    corridor_hits = 0
    aligned_hits = 0
    fff4_hits = 0
    family131_values: dict[str, int] = {}
    family260_values: dict[str, int] = {}

    for frame in frames_116:
        fam131 = frame.family131
        fam260 = frame.family260
        if fam131:
            family131_values[fam131] = family131_values.get(fam131, 0) + 1
        if fam260:
            family260_values[fam260] = family260_values.get(fam260, 0) + 1
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
                top_tier_peak_count += 1
        if has_plateau and fam131 == TOP_TIER_ZONE and fam260 == EXIT_ZONE:
            has_exit = True

    grade = "D"
    if has_seed and has_ramp and has_plateau and has_exit:
        grade = "A"
    elif has_seed:
        grade = "B"
    elif corridor_hits > 0:
        grade = "C"

    c45 = corr(control_vals, comp_b45)
    c67 = corr(control_vals, comp_b67)
    abs_b45 = None if c45 is None else abs(c45)
    abs_b67 = None if c67 is None else abs(c67)

    companion_mode = "insufficient"
    if c45 is not None and c67 is not None:
        if abs(c45) > abs(c67) + 0.05:
            companion_mode = "b4-b5"
        elif abs(c67) > abs(c45) + 0.05:
            companion_mode = "b6-b7"
        else:
            companion_mode = "dual"

    frame116_count = len(frames_116)
    corridor_ratio = corridor_hits / frame116_count if frame116_count else 0.0
    aligned_ratio = aligned_hits / frame116_count if frame116_count else 0.0
    fff4_ratio = fff4_hits / frame116_count if frame116_count else 0.0

    family131_primary = max(family131_values.items(), key=lambda kv: kv[1])[0] if family131_values else ""
    family260_primary = max(family260_values.items(), key=lambda kv: kv[1])[0] if family260_values else ""

    joined_strength = joined_lifecycle_strength(has_seed, has_ramp, has_plateau, has_exit)
    ladder = ladder_level(grade, has_seed, has_ramp, has_plateau, has_exit, corridor_ratio)
    value_type = classify_value_type(grade, has_seed, has_ramp, has_plateau, companion_mode, abs_b45, abs_b67)

    # The current automatic sweep does not infer transition overlays reliably.
    disengage_present = ""
    lane_change_present = ""
    active_core_present = ""
    late_stop_present = ""

    return {
        "sample_id": path.stem,
        "sample_path": str(path),
        "value_type_primary": value_type,
        "ladder_level": ladder,
        "grade": grade,
        "frame116_count": frame116_count,
        "duration_min": "" if first_ts is None or last_ts is None else round((last_ts - first_ts) / 60000.0, 2),
        "seed_touch_present": int(has_seed),
        "ramp_present": int(has_ramp),
        "phase_plateau_present": int(has_plateau),
        "phase_exit_present": int(has_exit),
        "joined_lifecycle_strength": joined_strength,
        "family_131_primary_zone": zone_bucket(family131_primary),
        "family_260_primary_zone": zone_bucket(family260_primary),
        "family_131_260_aligned": ordinal_from_ratio(aligned_ratio),
        "family_fff4_presence": ordinal_from_ratio(fff4_ratio),
        "corridor_match_strength": ordinal_from_ratio(corridor_ratio),
        "id_2e4_activity_level": 0 if total_bus0_rows == 0 else ordinal_from_ratio(count_2e4 / total_bus0_rows),
        "id_d8_structural_reference_strength": 0 if total_bus0_rows == 0 else ordinal_from_ratio(count_d8 / total_bus0_rows),
        "companion_primary_mode": companion_mode,
        "companion_b45_abs_corr": "" if abs_b45 is None else round(abs_b45, 3),
        "companion_b67_abs_corr": "" if abs_b67 is None else round(abs_b67, 3),
        "disengage_suspect_present": disengage_present,
        "lane_change_transition_present": lane_change_present,
        "active_core_present": active_core_present,
        "late_stop_present": late_stop_present,
        "bridge_candidate": "yes" if ladder == "4.5_candidate" else "no",
        "top_tier_peak_count": top_tier_peak_count,
        "parse_errors": parse_errors,
        "notes": "",
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)


def main() -> int:
    args = parse_args()
    files = iter_ndjson_files(args.inputs)
    if not files:
        raise SystemExit("No .ndjson files found.")

    rows = [analyze_file(path, args.bus) for path in files]

    fieldnames = [
        "sample_id",
        "sample_path",
        "value_type_primary",
        "ladder_level",
        "grade",
        "frame116_count",
        "duration_min",
        "seed_touch_present",
        "ramp_present",
        "phase_plateau_present",
        "phase_exit_present",
        "joined_lifecycle_strength",
        "family_131_primary_zone",
        "family_260_primary_zone",
        "family_131_260_aligned",
        "family_fff4_presence",
        "corridor_match_strength",
        "id_2e4_activity_level",
        "id_d8_structural_reference_strength",
        "companion_primary_mode",
        "companion_b45_abs_corr",
        "companion_b67_abs_corr",
        "disengage_suspect_present",
        "lane_change_transition_present",
        "active_core_present",
        "late_stop_present",
        "bridge_candidate",
        "top_tier_peak_count",
        "parse_errors",
        "notes",
    ]

    output_dir = Path(args.output_dir)
    all_csv = output_dir / "all_ndjson_feature_table.csv"
    all_json = output_dir / "all_ndjson_feature_table.json"
    valuable_csv = output_dir / "valuable_ndjson_feature_table.csv"
    valuable_json = output_dir / "valuable_ndjson_feature_table.json"

    write_csv(all_csv, rows, fieldnames)
    write_json(all_json, rows)

    valuable_rows = [
        row for row in rows
        if (
            row["grade"] in {"A", "B", "C"}
            or row["joined_lifecycle_strength"] > 0
            or row["corridor_match_strength"] > 0
            or row["companion_primary_mode"] in {"b4-b5", "b6-b7", "dual"}
        )
    ]
    write_csv(valuable_csv, valuable_rows, fieldnames)
    write_json(valuable_json, valuable_rows)

    print(f"all rows: {len(rows)}")
    print(f"valuable rows: {len(valuable_rows)}")
    print(f"all csv: {all_csv}")
    print(f"valuable csv: {valuable_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
