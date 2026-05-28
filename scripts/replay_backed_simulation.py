#!/usr/bin/env python3
"""
Replay-backed control-side simulation harness.

This script is intentionally conservative:
- it treats the current 0x260 mapping as a working hypothesis
- it replays against representative real logs
- it compares simulated slew-limited output to observed decoded setpoints

It does NOT claim implementation-ready integration.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


DEFAULT_SAMPLES: list[tuple[str, str, str]] = [
    ("anchor_190101", "anchor", r"<LOCAL_RAW_CAN_LOG>\toyota_seg_IGN_ON_20260312_190101_000.ndjson"),
    ("partial_171414", "partial_ramp", r"<LOCAL_RAW_CAN_LOG>\20260316\raw_can_logs\toyota_seg_IGN_ON_20260315_171414_000.ndjson"),
    ("compact_184921", "compact_partial", r"<LOCAL_RAW_CAN_LOG>\toyota_seg_IGN_ON_20260311_184921_000.ndjson"),
    ("city_20260418_a", "city_active", r"<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_all_20260418_163135_000.ndjson"),
    ("city_20260418_b", "city_hold", r"<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_all_20260418_175240_000.ndjson"),
    ("entry_20260426_s1", "entry_side", r"<LOCAL_RAW_CAN_LOG>\20260426\raw_can_logs\toyota_all_20260426_015302_000.ndjson"),
    ("entry_20260426_s2", "entry_side", r"<LOCAL_RAW_CAN_LOG>\20260426\raw_can_logs\toyota_all_20260426_042139_000.ndjson"),
    ("entry_20260426_s3", "entry_side", r"<LOCAL_RAW_CAN_LOG>\20260426\raw_can_logs\toyota_all_20260426_053902_000.ndjson"),
]


@dataclass(frozen=True)
class WindowSpec:
    mode: str | None
    value: float | None


@dataclass(frozen=True)
class SampleSpec:
    label: str
    regime: str
    path: Path
    window_start: WindowSpec
    window_end: WindowSpec


NEUTRAL = 289.0
LIMIT_NEG = -760.0
LIMIT_POS = 7981.0
SCALE_POS = LIMIT_POS - NEUTRAL
SCALE_NEG = NEUTRAL - LIMIT_NEG


def parse_hex(data: str) -> list[int]:
    return [int(data[i : i + 2], 16) for i in range(0, len(data), 2)]


def s16le(buf: list[int], idx: int) -> int:
    v = buf[idx] | (buf[idx + 1] << 8)
    return v - 65536 if v & 0x8000 else v


def s8(v: int) -> int:
    return v - 256 if v >= 128 else v


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return float(values[0])
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(xs[lo])
    frac = pos - lo
    return float(xs[lo] * (1 - frac) + xs[hi] * frac)


def parse_window_token(token: str | None) -> WindowSpec:
    if token is None or token == "":
        return WindowSpec(None, None)
    lowered = token.lower()
    if lowered.startswith("rel:"):
        return WindowSpec("rel", float(token.split(":", 1)[1]))
    if lowered.startswith("abs:"):
        return WindowSpec("abs", float(token.split(":", 1)[1]))
    raise ValueError(f"Invalid window token: {token}")


def window_label(start: WindowSpec, end: WindowSpec) -> str:
    if start.mode is None and end.mode is None:
        return "full"
    return f"{start.mode or 'open'}:{start.value if start.value is not None else ''}->{end.mode or 'open'}:{end.value if end.value is not None else ''}"


def decode_control_260(buf: list[int], decode_mode: str = "legacy_ff_negative") -> float:
    fine = s16le(buf, 2)
    value = fine + (s8(buf[5]) << 8)
    if decode_mode == "legacy_ff_negative":
        # Current best working branch: B1 participates in sign/domain.
        # We keep the older "0xFF means negative domain" assumption as replay hypothesis only.
        if buf[1] == 0xFF:
            value = -value
    elif decode_mode == "no_b1_flip":
        # Alternative replay branch: ignore B1 sign/domain flip entirely.
        value = value
    else:
        raise ValueError(f"Unknown decode mode: {decode_mode}")
    return float(value)


def normalize_path_for_runtime(raw_path: str | Path) -> Path:
    text = str(raw_path)
    # When running inside WSL/Linux, convert Windows drive paths to /mnt/<drive>/...
    if os.name != "nt":
        m = re.match(r"^([A-Za-z]):\\(.*)$", text)
        if m:
            drive = m.group(1).lower()
            tail = m.group(2).replace("\\", "/")
            return Path(f"/mnt/{drive}/{tail}")
    return Path(text)


def request_from_setpoint(setpoint: float, clamp: bool = True) -> float:
    if setpoint >= NEUTRAL:
        req = (setpoint - NEUTRAL) / SCALE_POS if SCALE_POS else 0.0
    else:
        req = (setpoint - NEUTRAL) / SCALE_NEG if SCALE_NEG else 0.0
    if clamp:
        return max(-1.0, min(1.0, req))
    return req


def map_request(req: float, bounded: bool = True) -> float:
    if req >= 0:
        val = NEUTRAL + (req * SCALE_POS)
        if bounded:
            return max(NEUTRAL, min(LIMIT_POS, val))
        return val
    val = NEUTRAL + (req * SCALE_NEG)
    if bounded:
        return max(LIMIT_NEG, min(NEUTRAL, val))
    return val


def apply_slew(series: list[float], slew_limit: float) -> list[float]:
    if not series:
        return []
    out = [series[0]]
    current = series[0]
    for target in series[1:]:
        diff = target - current
        if abs(diff) > slew_limit:
            current += math.copysign(slew_limit, diff)
        else:
            current = target
        out.append(current)
    return out


def mean_abs(xs: list[float]) -> float:
    return mean(abs(x) for x in xs) if xs else 0.0


def apply_window(
    ts_ms: list[int],
    control: list[float],
    start: WindowSpec,
    end: WindowSpec,
) -> tuple[list[int], list[float]]:
    if not ts_ms:
        return ts_ms, control

    start_bound = None
    end_bound = None
    first_ts = float(ts_ms[0])

    if start.mode == "abs":
        start_bound = start.value
    elif start.mode == "rel":
        start_bound = first_ts + (start.value * 1000.0)

    if end.mode == "abs":
        end_bound = end.value
    elif end.mode == "rel":
        end_bound = first_ts + (end.value * 1000.0)

    out_ts: list[int] = []
    out_control: list[float] = []
    for ts, val in zip(ts_ms, control):
        tsf = float(ts)
        if start_bound is not None and tsf < start_bound:
            continue
        if end_bound is not None and tsf >= end_bound:
            continue
        out_ts.append(ts)
        out_control.append(val)
    return out_ts, out_control


def load_control_series(
    path: Path,
    decode_mode: str = "legacy_ff_negative",
    window_start: WindowSpec | None = None,
    window_end: WindowSpec | None = None,
) -> tuple[list[int], list[float], int]:
    path = normalize_path_for_runtime(path)
    ts_ms: list[int] = []
    control: list[float] = []
    parse_errors = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                parse_errors += 1
                continue
            if row.get("bus") != 0 or row.get("addr") != 0x260:
                continue
            try:
                buf = parse_hex(row["data"])
                ts_ms.append(int(row["ts_ms"]))
                control.append(decode_control_260(buf, decode_mode=decode_mode))
            except Exception:
                parse_errors += 1
    start = window_start or WindowSpec(None, None)
    end = window_end or WindowSpec(None, None)
    ts_ms, control = apply_window(ts_ms, control, start, end)
    return ts_ms, control, parse_errors


def summarize_sample(sample: SampleSpec, decode_mode: str) -> dict[str, object]:
    ts_ms, control, parse_errors = load_control_series(
        sample.path,
        decode_mode=decode_mode,
        window_start=sample.window_start,
        window_end=sample.window_end,
    )
    deltas = [control[i] - control[i - 1] for i in range(1, len(control))]
    abs_deltas = [abs(x) for x in deltas]
    neutral_band = [x for x in control if abs(x - NEUTRAL) <= 25]
    return {
        "sample_id": sample.label,
        "regime": sample.regime,
        "decode_mode": decode_mode,
        "sample_path": str(sample.path),
        "window": window_label(sample.window_start, sample.window_end),
        "frames_260": len(control),
        "duration_min": round((ts_ms[-1] - ts_ms[0]) / 60000.0, 2) if len(ts_ms) >= 2 else 0.0,
        "parse_errors": parse_errors,
        "min_setpoint": round(min(control), 3) if control else None,
        "max_setpoint": round(max(control), 3) if control else None,
        "p05_setpoint": round(percentile(control, 0.05), 3) if control else None,
        "p50_setpoint": round(percentile(control, 0.50), 3) if control else None,
        "p95_setpoint": round(percentile(control, 0.95), 3) if control else None,
        "neutral_band_ratio": round(len(neutral_band) / len(control), 3) if control else None,
        "max_abs_delta": round(max(abs_deltas), 3) if abs_deltas else None,
        "avg_abs_delta": round(mean(abs_deltas), 3) if abs_deltas else None,
        "p95_abs_delta": round(percentile(abs_deltas, 0.95), 3) if abs_deltas else None,
        "positive_ratio": round(sum(1 for x in control if x > NEUTRAL) / len(control), 3) if control else None,
        "negative_ratio": round(sum(1 for x in control if x < NEUTRAL) / len(control), 3) if control else None,
    }


def build_target_series(control: list[float], mode: str) -> list[float]:
    if mode == "identity":
        return list(control)
    if mode == "bounded":
        derived_requests = [request_from_setpoint(x, clamp=True) for x in control]
        return [map_request(r, bounded=True) for r in derived_requests]
    if mode == "unbounded":
        derived_requests = [request_from_setpoint(x, clamp=False) for x in control]
        return [map_request(r, bounded=False) for r in derived_requests]
    raise ValueError(f"Unknown replay mode: {mode}")


def replay_sample(sample: SampleSpec, slew_limit: float, mode: str, decode_mode: str) -> dict[str, object]:
    _, control, parse_errors = load_control_series(
        sample.path,
        decode_mode=decode_mode,
        window_start=sample.window_start,
        window_end=sample.window_end,
    )
    if len(control) < 3:
        return {
            "sample_id": sample.label,
            "regime": sample.regime,
            "decode_mode": decode_mode,
            "sample_path": str(sample.path),
            "window": window_label(sample.window_start, sample.window_end),
            "slew_limit": slew_limit,
            "mode": mode,
            "parse_errors": parse_errors,
            "frames_260": len(control),
            "status": "insufficient",
        }

    mapped_targets = build_target_series(control, mode)
    replayed = apply_slew(mapped_targets, slew_limit)

    point_errors = [replayed[i] - control[i] for i in range(len(control))]
    observed_delta = [control[i] - control[i - 1] for i in range(1, len(control))]
    replay_delta = [replayed[i] - replayed[i - 1] for i in range(1, len(replayed))]
    delta_errors = [replay_delta[i] - observed_delta[i] for i in range(len(observed_delta))]

    oversmoothed = 0
    undersmoothed = 0
    for obs, sim in zip(observed_delta, replay_delta):
        if abs(sim) + 1e-9 < abs(obs):
            oversmoothed += 1
        elif abs(sim) - 1e-9 > abs(obs):
            undersmoothed += 1

    return {
        "sample_id": sample.label,
        "regime": sample.regime,
        "decode_mode": decode_mode,
        "sample_path": str(sample.path),
        "window": window_label(sample.window_start, sample.window_end),
        "slew_limit": slew_limit,
        "mode": mode,
        "parse_errors": parse_errors,
        "frames_260": len(control),
        "status": "ok",
        "point_mae": round(mean_abs(point_errors), 3),
        "point_p95_abs_error": round(percentile([abs(x) for x in point_errors], 0.95), 3),
        "delta_mae": round(mean_abs(delta_errors), 3),
        "delta_p95_abs_error": round(percentile([abs(x) for x in delta_errors], 0.95), 3),
        "oversmoothed_ratio": round(oversmoothed / len(observed_delta), 3),
        "undersmoothed_ratio": round(undersmoothed / len(observed_delta), 3),
        "target_pos_saturation_ratio": round(sum(1 for x in mapped_targets if x >= LIMIT_POS) / len(mapped_targets), 3),
        "target_neg_saturation_ratio": round(sum(1 for x in mapped_targets if x <= LIMIT_NEG) / len(mapped_targets), 3),
        "replay_pos_saturation_ratio": round(sum(1 for x in replayed if x >= LIMIT_POS) / len(replayed), 3),
        "replay_neg_saturation_ratio": round(sum(1 for x in replayed if x <= LIMIT_NEG) / len(replayed), 3),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sanitize_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay-backed simulation harness for Toyota Sienna control-side hypotheses.")
    parser.add_argument(
        "--sample",
        action="append",
        help="Custom sample in form label|regime|absolute_path[|rel:start_s|rel:end_s] or with abs:<ts_ms>. May be repeated. If omitted, built-in representative set is used.",
    )
    parser.add_argument(
        "--slew",
        action="append",
        type=float,
        help="Slew limit candidate. May be repeated. Defaults to 10,25,50,75,100.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "analysis-output" / "replay_simulation"),
        help="Directory for CSV outputs.",
    )
    parser.add_argument(
        "--mode",
        action="append",
        choices=["bounded", "unbounded", "identity"],
        help="Replay mode. May be repeated. Defaults to bounded,unbounded,identity.",
    )
    parser.add_argument(
        "--decode-mode",
        action="append",
        choices=["legacy_ff_negative", "no_b1_flip"],
        help="Decode branch to compare. May be repeated. Defaults to both legacy_ff_negative and no_b1_flip.",
    )
    parser.add_argument(
        "--emit-trace",
        action="store_true",
        help="Emit per-frame replay traces for each selected sample/mode/slew/decode combination.",
    )
    return parser.parse_args()


def resolve_samples(args: argparse.Namespace) -> list[SampleSpec]:
    if not args.sample:
        return [
            SampleSpec(
                label=label,
                regime=regime,
                path=normalize_path_for_runtime(path),
                window_start=WindowSpec(None, None),
                window_end=WindowSpec(None, None),
            )
            for label, regime, path in DEFAULT_SAMPLES
        ]
    out: list[SampleSpec] = []
    for raw in args.sample:
        parts = raw.split("|")
        if len(parts) not in (3, 5):
            raise ValueError(f"Invalid --sample format: {raw}")
        label, regime, path = parts[:3]
        start = parse_window_token(parts[3]) if len(parts) == 5 else WindowSpec(None, None)
        end = parse_window_token(parts[4]) if len(parts) == 5 else WindowSpec(None, None)
        out.append(
            SampleSpec(
                label=label,
                regime=regime,
                path=normalize_path_for_runtime(path),
                window_start=start,
                window_end=end,
            )
        )
    return out


def main() -> None:
    args = parse_args()
    samples = resolve_samples(args)
    slew_limits = args.slew or [10.0, 25.0, 50.0, 75.0, 100.0]
    modes = args.mode or ["bounded", "unbounded", "identity"]
    decode_modes = args.decode_mode or ["legacy_ff_negative", "no_b1_flip"]

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    sample_rows = [
        summarize_sample(sample, decode_mode)
        for sample in samples
        for decode_mode in decode_modes
    ]
    replay_rows: list[dict[str, object]] = []
    for sample in samples:
        for decode_mode in decode_modes:
            for mode in modes:
                for slew in slew_limits:
                    replay_rows.append(replay_sample(sample, slew, mode, decode_mode))

    write_csv(outdir / "mapping_replay_summary.csv", sample_rows)
    write_csv(outdir / "slew_replay_summary.csv", replay_rows)

    if args.emit_trace:
        trace_dir = outdir / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        for sample in samples:
            for decode_mode in decode_modes:
                ts_ms, control, _ = load_control_series(
                    sample.path,
                    decode_mode=decode_mode,
                    window_start=sample.window_start,
                    window_end=sample.window_end,
                )
                if len(control) < 2:
                    continue
                for mode in modes:
                    mapped_targets = build_target_series(control, mode)
                    for slew in slew_limits:
                        replayed = apply_slew(mapped_targets, slew)
                        rows: list[dict[str, object]] = []
                        for idx, (ts, observed, target, replayed_value) in enumerate(zip(ts_ms, control, mapped_targets, replayed)):
                            point_error = replayed_value - observed
                            obs_delta = None
                            sim_delta = None
                            delta_error = None
                            if idx > 0:
                                obs_delta = observed - control[idx - 1]
                                sim_delta = replayed_value - replayed[idx - 1]
                                delta_error = sim_delta - obs_delta
                            rows.append(
                                {
                                    "index": idx,
                                    "ts_ms": ts,
                                    "sample_id": sample.label,
                                    "regime": sample.regime,
                                    "window": window_label(sample.window_start, sample.window_end),
                                    "decode_mode": decode_mode,
                                    "mode": mode,
                                    "slew_limit": slew,
                                    "observed_setpoint": round(observed, 6),
                                    "target_setpoint": round(target, 6),
                                    "replayed_setpoint": round(replayed_value, 6),
                                    "point_error": round(point_error, 6),
                                    "observed_delta": round(obs_delta, 6) if obs_delta is not None else None,
                                    "replayed_delta": round(sim_delta, 6) if sim_delta is not None else None,
                                    "delta_error": round(delta_error, 6) if delta_error is not None else None,
                                }
                            )
                        filename = (
                            f"{sanitize_name(sample.label)}__{sanitize_name(decode_mode)}__"
                            f"{sanitize_name(mode)}__slew_{int(slew) if float(slew).is_integer() else sanitize_name(str(slew))}.csv"
                        )
                        write_csv(trace_dir / filename, rows)

    manifest = {
        "samples": [
            {
                "sample_id": sample.label,
                "regime": sample.regime,
                "sample_path": str(sample.path),
                "window": window_label(sample.window_start, sample.window_end),
            }
            for sample in samples
        ],
        "decode_modes": decode_modes,
        "slew_limits": slew_limits,
        "modes": modes,
        "emit_trace": args.emit_trace,
        "output_dir": str(outdir),
    }
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps({
        "samples": len(samples),
        "decode_modes": decode_modes,
        "slew_limits": slew_limits,
        "modes": modes,
        "mapping_summary": str(outdir / "mapping_replay_summary.csv"),
        "slew_summary": str(outdir / "slew_replay_summary.csv"),
    }, indent=2))


if __name__ == "__main__":
    main()
