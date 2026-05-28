#!/usr/bin/env python3
"""
Validate the current replay-backed control-side branch on bridge-target ladder windows.

Compares:
- bounded
- identity

under:
- decode_mode = no_b1_flip
- slew = 175
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from replay_backed_simulation import (
    SampleSpec,
    WindowSpec,
    build_target_series,
    load_control_series,
    percentile,
    write_csv,
)


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "analysis-output" / "bridge_target_control_branch_validation"

SAMPLES: list[SampleSpec] = [
    SampleSpec(
        label="early_185520_seed_touch",
        regime="seed_touch_only",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\toyota_seg_IGN_ON_20260312_185520_000.ndjson"),
        window_start=WindowSpec("rel", 15.0),
        window_end=WindowSpec("rel", 30.0),
    ),
    SampleSpec(
        label="bridge_173834_primary_ramp",
        regime="ramping_bridge",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\20260314\raw_can_logs\toyota_seg_IGN_ON_20260314_173834_000.ndjson"),
        window_start=WindowSpec("rel", 180.0),
        window_end=WindowSpec("rel", 195.0),
    ),
    SampleSpec(
        label="compact_184921_ramp",
        regime="compact_partial",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\toyota_seg_IGN_ON_20260311_184921_000.ndjson"),
        window_start=WindowSpec("rel", 90.0),
        window_end=WindowSpec("rel", 105.0),
    ),
    SampleSpec(
        label="partial_171414_ramp",
        regime="partial_ramp",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\20260316\raw_can_logs\toyota_seg_IGN_ON_20260315_171414_000.ndjson"),
        window_start=WindowSpec("rel", 390.0),
        window_end=WindowSpec("rel", 420.0),
    ),
    SampleSpec(
        label="anchor_190101_window",
        regime="anchor_window",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\toyota_seg_IGN_ON_20260312_190101_000.ndjson"),
        window_start=WindowSpec("abs", 1773342240000.0),
        window_end=WindowSpec("abs", 1773342255000.0),
    ),
]

VARIANTS = [
    {"name": "bounded_175", "mode": "bounded", "slew": 175.0},
    {"name": "identity_175", "mode": "identity", "slew": 175.0},
]


def apply_slew(series: list[float], base_slew: float) -> list[float]:
    if not series:
        return []
    out = [series[0]]
    current = series[0]
    for target in series[1:]:
        diff = target - current
        if abs(diff) > base_slew:
            current += math.copysign(base_slew, diff)
        else:
            current = target
        out.append(current)
    return out


def mean_abs(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(abs(v) for v in values) / len(values)


def run() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    for sample in SAMPLES:
        _, control, parse_errors = load_control_series(
            sample.path,
            decode_mode="no_b1_flip",
            window_start=sample.window_start,
            window_end=sample.window_end,
        )
        for variant in VARIANTS:
            targets = build_target_series(control, variant["mode"])
            replayed = apply_slew(targets, float(variant["slew"]))
            point_errors = [replayed[i] - control[i] for i in range(len(control))]
            observed_delta = [control[i] - control[i - 1] for i in range(1, len(control))]
            replay_delta = [replayed[i] - replayed[i - 1] for i in range(1, len(replayed))]
            delta_errors = [replay_delta[i] - observed_delta[i] for i in range(len(observed_delta))]
            rows.append(
                {
                    "sample_id": sample.label,
                    "regime": sample.regime,
                    "variant": variant["name"],
                    "mode": variant["mode"],
                    "slew": variant["slew"],
                    "frames_260": len(control),
                    "observed_min": round(min(control), 3) if control else None,
                    "observed_max": round(max(control), 3) if control else None,
                    "point_mae": round(mean_abs(point_errors), 3),
                    "point_p95_abs_error": round(percentile([abs(x) for x in point_errors], 0.95), 3),
                    "delta_mae": round(mean_abs(delta_errors), 3),
                    "delta_p95_abs_error": round(percentile([abs(x) for x in delta_errors], 0.95), 3),
                    "parse_errors": parse_errors,
                }
            )

    write_csv(OUTPUT_DIR / "summary.csv", rows)
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(
            {
                "samples": [
                    {"sample_id": s.label, "regime": s.regime, "path": str(s.path)}
                    for s in SAMPLES
                ],
                "variants": VARIANTS,
                "output_dir": str(OUTPUT_DIR),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"summary": str(OUTPUT_DIR / "summary.csv")}, indent=2))


if __name__ == "__main__":
    run()
