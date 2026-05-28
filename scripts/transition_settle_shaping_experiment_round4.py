#!/usr/bin/env python3
"""
Round 4 shaping experiment for the settle-tail sub-phase.

This round narrows entirely onto the current best lever:
- low-band catch-up

It sweeps a tighter range of low-band boosts to find the best local region.
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


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "analysis-output" / "transition_settle_shaping_experiment_round4"


SAMPLES: list[SampleSpec] = [
    SampleSpec(
        label="city_20260418_late_stop_approach",
        regime="city_approach_window",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_seg_IGN_ON_20260418_181012_007.ndjson"),
        window_start=WindowSpec("rel", 0.0),
        window_end=WindowSpec("rel", 29.0),
    ),
    SampleSpec(
        label="city_20260418_transition_settle_tail",
        regime="city_transition_settle_tail",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_seg_IGN_ON_20260418_181012_007.ndjson"),
        window_start=WindowSpec("rel", 44.0),
        window_end=WindowSpec("rel", 59.0),
    ),
    SampleSpec(
        label="city_20260418_final_hold",
        regime="city_final_hold_window",
        path=Path(r"<LOCAL_RAW_CAN_LOG>\20260418\raw_can_logs\toyota_seg_IGN_ON_20260418_181012_007.ndjson"),
        window_start=WindowSpec("rel", 59.0),
        window_end=WindowSpec("rel", 89.0),
    ),
]


VARIANTS = [
    {"name": "baseline", "slew": 175.0, "regime_gate": None, "low_band_limit": None, "low_band_boost": 1.0},
    {"name": "low_band_catchup_2p50", "slew": 175.0, "regime_gate": "city_transition_settle_tail", "low_band_limit": 100.0, "low_band_boost": 2.5},
    {"name": "low_band_catchup_3p00", "slew": 175.0, "regime_gate": "city_transition_settle_tail", "low_band_limit": 100.0, "low_band_boost": 3.0},
    {"name": "low_band_catchup_3p50", "slew": 175.0, "regime_gate": "city_transition_settle_tail", "low_band_limit": 100.0, "low_band_boost": 3.5},
    {"name": "low_band_catchup_4p00", "slew": 175.0, "regime_gate": "city_transition_settle_tail", "low_band_limit": 100.0, "low_band_boost": 4.0},
]


def apply_variant_slew(
    sample: SampleSpec,
    series: list[float],
    base_slew: float,
    regime_gate: str | None,
    low_band_limit: float | None,
    low_band_boost: float,
) -> list[float]:
    if not series:
        return []
    out = [series[0]]
    current = series[0]
    for target in series[1:]:
        diff = target - current
        effective = base_slew
        gated = regime_gate is None or sample.regime == regime_gate
        if gated and low_band_limit is not None and abs(target) <= low_band_limit and abs(diff) > base_slew:
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
            replayed = apply_variant_slew(
                sample=sample,
                series=targets,
                base_slew=float(variant["slew"]),
                regime_gate=variant["regime_gate"],
                low_band_limit=variant["low_band_limit"],
                low_band_boost=float(variant["low_band_boost"]),
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
                    "base_slew": variant["slew"],
                    "regime_gate": variant["regime_gate"],
                    "low_band_limit": variant["low_band_limit"],
                    "low_band_boost": variant["low_band_boost"],
                    "parse_errors": parse_errors,
                    "frames_260": len(control),
                    "point_mae": round(mean_abs(point_errors), 3),
                    "point_p95_abs_error": round(percentile([abs(x) for x in point_errors], 0.95), 3),
                    "delta_mae": round(mean_abs(delta_errors), 3),
                    "delta_p95_abs_error": round(percentile([abs(x) for x in delta_errors], 0.95), 3),
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
    print(json.dumps({"summary": str(OUTPUT_DIR / 'summary.csv')}, indent=2))


if __name__ == "__main__":
    run()
