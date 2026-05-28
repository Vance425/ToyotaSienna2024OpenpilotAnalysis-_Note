#!/usr/bin/env python3
"""
Validate the current city-side working rule on a second city transition sample.

Sample source:
- 2026-04-18 Session 1 late segment
- toyota_seg_IGN_ON_20260418_163943_003.ndjson

Windows:
- rel 120-130: dynamic pre-settle approach
- rel 130-140: second transition/settle candidate
- rel 140-150: negative post-settle / hold-like tail
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


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "analysis-output" / "transition_settle_second_city_validation"

SAMPLES: list[SampleSpec] = [
    SampleSpec(
        label="city2_20260418_pre_settle",
        regime="city2_pre_settle_window",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_seg_IGN_ON_20260418_163943_003.ndjson"),
        window_start=WindowSpec("rel", 120.0),
        window_end=WindowSpec("rel", 130.0),
    ),
    SampleSpec(
        label="city2_20260418_transition_settle",
        regime="city2_transition_settle_window",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_seg_IGN_ON_20260418_163943_003.ndjson"),
        window_start=WindowSpec("rel", 130.0),
        window_end=WindowSpec("rel", 140.0),
    ),
    SampleSpec(
        label="city2_20260418_post_settle_hold",
        regime="city2_post_settle_hold_window",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_seg_IGN_ON_20260418_163943_003.ndjson"),
        window_start=WindowSpec("rel", 140.0),
        window_end=WindowSpec("rel", 150.0),
    ),
]

VARIANTS = [
    {
        "name": "baseline",
        "slew": 175.0,
        "low_band_limit": None,
        "low_band_boost": 1.0,
        "deep_band_limit": None,
        "deep_band_boost": 1.0,
    },
    {
        "name": "low_band_catchup_5p50",
        "slew": 175.0,
        "low_band_limit": 100.0,
        "low_band_boost": 5.5,
        "deep_band_limit": None,
        "deep_band_boost": 1.0,
    },
    {
        "name": "low55_plus_deep2p50",
        "slew": 175.0,
        "low_band_limit": 100.0,
        "low_band_boost": 5.5,
        "deep_band_limit": 700.0,
        "deep_band_boost": 2.5,
    },
]


def apply_variant(sample: SampleSpec, series: list[float], base_slew: float, low_band_limit: float | None, low_band_boost: float, deep_band_limit: float | None, deep_band_boost: float) -> list[float]:
    if not series:
        return []
    out = [series[0]]
    current = series[0]
    for target in series[1:]:
        diff = target - current
        effective = base_slew
        is_transition_like = sample.regime == "city2_transition_settle_window"
        if is_transition_like:
            if low_band_limit is not None and abs(target) <= low_band_limit and abs(diff) > base_slew:
                effective = max(effective, base_slew * low_band_boost)
            if deep_band_limit is not None and target <= -deep_band_limit and abs(diff) > base_slew:
                effective = max(effective, base_slew * deep_band_boost)
        if abs(diff) > effective:
            current += math.copysign(effective, diff)
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
        targets = build_target_series(control, "identity")
        for variant in VARIANTS:
            replayed = apply_variant(
                sample,
                targets,
                float(variant["slew"]),
                variant["low_band_limit"],
                float(variant["low_band_boost"]),
                variant["deep_band_limit"],
                float(variant["deep_band_boost"]),
            )
            point_errors = [replayed[i] - control[i] for i in range(len(control))]
            observed_delta = [control[i] - control[i - 1] for i in range(1, len(control))]
            replay_delta = [replayed[i] - replayed[i - 1] for i in range(1, len(replayed))]
            delta_errors = [replay_delta[i] - observed_delta[i] for i in range(len(observed_delta))]
            rows.append(
                {
                    "sample_id": sample.label,
                    "regime": sample.regime,
                    "variant": variant["name"],
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
