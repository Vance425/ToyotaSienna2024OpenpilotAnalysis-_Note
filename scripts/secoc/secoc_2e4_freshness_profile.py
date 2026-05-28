#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Profile Toyota SecOC synchronization and 0x2E4 freshness hints from ndjson logs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SYNC_ADDR = 0x0F
STEERING_LKA_ADDR = 0x2E4


@dataclass
class SyncState:
    ts_ms: int
    bus: int
    trip_cnt: int
    reset_cnt: int
    authenticator: int
    data: str


@dataclass
class LkaFrame:
    ts_ms: int
    bus: int
    data: str
    prefix_hex: str
    flags_nibble: int
    msg_cnt_low2: int
    reset_low2: int
    authenticator: int
    trip_cnt: int | None
    reset_cnt: int | None
    sync_age_ms: int | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="ndjson files or directories containing ndjson files.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated summary files.")
    parser.add_argument("--file-glob", action="append", default=["*.ndjson"], help="Glob used for directory inputs.")
    parser.add_argument("--addr", default="0x2e4", help="Protected frame address to profile. Default: 0x2e4.")
    parser.add_argument("--sample-limit", type=int, default=20, help="Rows to include in sample CSV.")
    return parser.parse_args()


def parse_addr(text: str) -> int:
    text = text.strip().lower()
    return int(text, 16) if text.startswith("0x") else int(text)


def iter_files(inputs: list[str], globs: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for pattern in globs:
                files.extend(sorted(path.glob(pattern)))
    return sorted(dict.fromkeys(files))


def decode_sync(data_hex: str, ts_ms: int, bus: int) -> SyncState | None:
    try:
        data = bytes.fromhex(data_hex)
    except ValueError:
        return None
    if len(data) != 8:
        return None
    trip_cnt = (data[0] << 8) | data[1]
    reset_cnt = (data[2] << 12) | (data[3] << 4) | (data[4] >> 4)
    authenticator = ((data[4] & 0x0F) << 24) | (data[5] << 16) | (data[6] << 8) | data[7]
    return SyncState(ts_ms, bus, trip_cnt, reset_cnt, authenticator, data_hex)


def decode_protected(data_hex: str, ts_ms: int, bus: int, sync: SyncState | None) -> LkaFrame | None:
    try:
        data = bytes.fromhex(data_hex)
    except ValueError:
        return None
    if len(data) != 8:
        return None
    flags = data[4] >> 4
    auth = ((data[4] & 0x0F) << 24) | (data[5] << 16) | (data[6] << 8) | data[7]
    return LkaFrame(
        ts_ms=ts_ms,
        bus=bus,
        data=data_hex,
        prefix_hex=data[:4].hex(),
        flags_nibble=flags,
        msg_cnt_low2=flags >> 2,
        reset_low2=flags & 0b11,
        authenticator=auth,
        trip_cnt=sync.trip_cnt if sync else None,
        reset_cnt=sync.reset_cnt if sync else None,
        sync_age_ms=(ts_ms - sync.ts_ms) if sync else None,
    )


def iter_events(files: Iterable[Path], target_addr: int):
    last_sync_by_bus: dict[int, SyncState] = {}
    for file_path in files:
        with file_path.open("r", encoding="utf-8", errors="replace") as f:
            for line_no, line in enumerate(f, 1):
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                addr = int(row.get("addr", -1))
                bus = int(row.get("bus", -1))
                ts_ms = int(row.get("ts_ms", 0))
                data_hex = str(row.get("data", "")).lower()
                if addr == SYNC_ADDR:
                    sync = decode_sync(data_hex, ts_ms, bus)
                    if sync:
                        last_sync_by_bus[bus] = sync
                        yield "sync", file_path, sync
                elif addr == target_addr:
                    frame = decode_protected(data_hex, ts_ms, bus, last_sync_by_bus.get(bus))
                    if frame:
                        yield "protected", file_path, frame


def run() -> None:
    args = parse_args()
    target_addr = parse_addr(args.addr)
    files = iter_files(args.inputs, args.file_glob)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sync_count_by_bus = Counter()
    sync_values_by_bus = defaultdict(Counter)
    sync_auth_by_trip_reset = defaultdict(set)
    protected_count_by_bus = Counter()
    flags_by_bus = defaultdict(Counter)
    reset_match = Counter()
    prefix_counts = Counter()
    prefix_flag_counts = Counter()
    sync_age_buckets = Counter()
    msg_low2_transitions = defaultdict(Counter)
    prev_low2_by_bus: dict[int, int] = {}
    samples: list[LkaFrame] = []

    for kind, file_path, event in iter_events(files, target_addr):
        if kind == "sync":
            sync: SyncState = event
            sync_count_by_bus[sync.bus] += 1
            sync_values_by_bus[sync.bus][(sync.trip_cnt, sync.reset_cnt)] += 1
            sync_auth_by_trip_reset[(sync.trip_cnt, sync.reset_cnt)].add(sync.authenticator)
            continue

        frame: LkaFrame = event
        protected_count_by_bus[frame.bus] += 1
        flags_by_bus[frame.bus][frame.flags_nibble] += 1
        prefix_counts[frame.prefix_hex] += 1
        prefix_flag_counts[(frame.prefix_hex, frame.flags_nibble)] += 1
        if frame.reset_cnt is None:
            reset_match["no_sync"] += 1
        elif (frame.reset_cnt & 0b11) == frame.reset_low2:
            reset_match["match"] += 1
        else:
            reset_match["mismatch"] += 1
        if frame.sync_age_ms is None:
            sync_age_buckets["no_sync"] += 1
        elif frame.sync_age_ms < 0:
            sync_age_buckets["negative"] += 1
        elif frame.sync_age_ms <= 1000:
            sync_age_buckets["0-1s"] += 1
        elif frame.sync_age_ms <= 5000:
            sync_age_buckets["1-5s"] += 1
        else:
            sync_age_buckets[">5s"] += 1
        prev = prev_low2_by_bus.get(frame.bus)
        if prev is not None:
            msg_low2_transitions[frame.bus][(prev, frame.msg_cnt_low2)] += 1
        prev_low2_by_bus[frame.bus] = frame.msg_cnt_low2
        if len(samples) < args.sample_limit:
            samples.append(frame)

    sample_csv = out_dir / "secoc_2e4_samples.csv"
    with sample_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ts_ms", "bus", "data", "prefix_hex", "flags_nibble", "msg_cnt_low2",
                "reset_low2", "authenticator_hex", "trip_cnt", "reset_cnt", "sync_age_ms",
            ],
        )
        writer.writeheader()
        for item in samples:
            writer.writerow({
                "ts_ms": item.ts_ms,
                "bus": item.bus,
                "data": item.data,
                "prefix_hex": item.prefix_hex,
                "flags_nibble": f"0x{item.flags_nibble:x}",
                "msg_cnt_low2": item.msg_cnt_low2,
                "reset_low2": item.reset_low2,
                "authenticator_hex": f"0x{item.authenticator:07x}",
                "trip_cnt": item.trip_cnt,
                "reset_cnt": item.reset_cnt,
                "sync_age_ms": item.sync_age_ms,
            })

    summary = {
        "files": [str(p) for p in files],
        "target_addr": f"0x{target_addr:x}",
        "sync_count_by_bus": dict(sync_count_by_bus),
        "protected_count_by_bus": dict(protected_count_by_bus),
        "reset_low2_match": dict(reset_match),
        "sync_age_buckets": dict(sync_age_buckets),
        "unique_sync_trip_reset_by_bus": {str(bus): len(counter) for bus, counter in sync_values_by_bus.items()},
        "sync_auth_variants_by_trip_reset": {
            f"{trip}:{reset}": len(auths)
            for (trip, reset), auths in list(sync_auth_by_trip_reset.items())[:100]
        },
        "flags_by_bus": {
            str(bus): {f"0x{flag:x}": count for flag, count in counter.most_common()}
            for bus, counter in flags_by_bus.items()
        },
        "top_prefixes": prefix_counts.most_common(20),
        "top_prefix_flag_pairs": [
            [prefix, f"0x{flag:x}", count]
            for (prefix, flag), count in prefix_flag_counts.most_common(30)
        ],
        "msg_low2_transitions": {
            str(bus): {f"{src}->{dst}": count for (src, dst), count in counter.most_common()}
            for bus, counter in msg_low2_transitions.items()
        },
    }
    summary_json = out_dir / "secoc_2e4_freshness_profile.json"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report_md = out_dir / "secoc_2e4_freshness_profile.md"
    lines = [
        "# 0x2E4 SecOC Freshness Profile",
        "",
        f"Files: `{len(files)}`",
        f"Target addr: `{target_addr:#x}`",
        "",
        "## Counts",
        "",
        f"- Sync `0x0F` by bus: `{dict(sync_count_by_bus)}`",
        f"- Protected target by bus: `{dict(protected_count_by_bus)}`",
        f"- Reset low2 check: `{dict(reset_match)}`",
        f"- Sync age buckets: `{dict(sync_age_buckets)}`",
        "",
        "## Flags",
        "",
    ]
    for bus, counter in sorted(flags_by_bus.items()):
        flags_text = ", ".join(f"0x{flag:x}:{count}" for flag, count in counter.most_common())
        lines.append(f"- bus{bus}: {flags_text}")
    lines.extend(["", "## Message Counter Low2 Transitions", ""])
    for bus, counter in sorted(msg_low2_transitions.items()):
        text = ", ".join(f"{src}->{dst}:{count}" for (src, dst), count in counter.most_common())
        lines.append(f"- bus{bus}: {text}")
    lines.extend(["", "## Top Prefixes", ""])
    for prefix, count in prefix_counts.most_common(12):
        lines.append(f"- `{prefix}`: {count}")
    lines.extend(["", "## Outputs", "", f"- `{summary_json}`", f"- `{sample_csv}`"])
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[INFO] files={len(files)} sync={sum(sync_count_by_bus.values())} protected={sum(protected_count_by_bus.values())}")
    print(f"[INFO] report={report_md}")
    print(f"[INFO] samples={sample_csv}")


if __name__ == "__main__":
    run()
