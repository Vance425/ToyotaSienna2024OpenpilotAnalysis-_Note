#!/usr/bin/env python3
"""
Residual breakdown for the city transition settle-tail shaping branch.

Compares:
- baseline
- low-band catch-up 4.5x
- low-band catch-up 5.5x

The goal is to see which observed sub-bands improve, and whether 5.5x is only
helping one residual cluster or broadly improving the settle-tail regime.
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


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "analysis-output" / "transition_settle_residual_breakdown"
SAMPLE = SampleSpec(
    label="city_20260418_transition_settle_tail",
    regime="city_transition_settle_tail",
    path=Path(r"<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_seg_IGN_ON_20260418_181012_007.ndjson"),
    window_start=WindowSpec("rel", 44.0),
    window_end=WindowSpec("rel", 59.0),
)

VARIANTS = [
    {"name": "baseline", "base_slew": 175.0, "low_band_limit": None, "low_band_boost": 1.0},
    {"name": "low_band_catchup_4p50", "base_slew": 175.0, "low_band_limit": 100.0, "low_band_boost": 4.5},
    {"name": "low_band_catchup_5p50", "base_slew": 175.0, "low_band_limit": 100.0, "low_band_boost": 5.5},
]


def apply_variant(series: list[float], base_slew: float, low_band_limit: float | None, low_band_boost: float) -> list[float]:
    if not series:
        return []
    out = [series[0]]
    current = series[0]
    for target in series[1:]:
        diff = target - current
        effective = base_slew
        if low_band_limit is not None and abs(target) <= low_band_limit and abs(diff) > base_slew:
            effective = max(effective, base_slew * low_band_boost)
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


def bucket_for_observed(value: float) -> str:
    if value <= -1500:
        return "deep_negative"
    if value <= -700:
        return "mid_negative"
    if value <= -100:
        return "low_negative"
    return "near_zero"


def run() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _, control, parse_errors = load_control_series(
        SAMPLE.path,
        decode_mode="no_b1_flip",
        window_start=SAMPLE.window_start,
        window_end=SAMPLE.window_end,
    )
    targets = build_target_series(control, "identity")

    detail_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for variant in VARIANTS:
        replayed = apply_variant(
            series=targets,
            base_slew=float(variant["base_slew"]),
            low_band_limit=variant["low_band_limit"],
            low_band_boost=float(variant["low_band_boost"]),
        )
        bucketed: dict[str, list[float]] = {}
        for idx, observed in enumerate(control):
            error = replayed[idx] - observed
            bucket = bucket_for_observed(observed)
            bucketed.setdefault(bucket, []).append(error)
            detail_rows.append(
                {
                    "sample_id": SAMPLE.label,
                    "variant": variant["name"],
                    "frame_index": idx,
                    "observed_setpoint": round(observed, 3),
                    "target_identity": round(targets[idx], 3),
                    "replayed_setpoint": round(replayed[idx], 3),
                    "error": round(error, 3),
                    "bucket": bucket,
                }
            )

        all_errors = [row["error"] for row in detail_rows if row["variant"] == variant["name"]]
        summary_rows.append(
            {
                "sample_id": SAMPLE.label,
                "variant": variant["name"],
                "bucket": "__all__",
                "frames": len(all_errors),
                "point_mae": round(mean_abs(all_errors), 3),
                "point_p95_abs_error": round(percentile([abs(x) for x in all_errors], 0.95), 3),
                "parse_errors": parse_errors,
            }
        )
        for bucket, errors in bucketed.items():
            summary_rows.append(
                {
                    "sample_id": SAMPLE.label,
                    "variant": variant["name"],
                    "bucket": bucket,
                    "frames": len(errors),
                    "point_mae": round(mean_abs(errors), 3),
                    "point_p95_abs_error": round(percentile([abs(x) for x in errors], 0.95), 3),
                    "parse_errors": parse_errors,
                }
            )

    write_csv(OUTPUT_DIR / "detail.csv", detail_rows)
    write_csv(OUTPUT_DIR / "summary.csv", summary_rows)
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(
            {
                "sample": {"sample_id": SAMPLE.label, "path": str(SAMPLE.path), "regime": SAMPLE.regime},
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
