#!/usr/bin/env python3
import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Feedback-targeted follow-up analysis for Toyota control model outputs. "
            "This script avoids self-fitting the decoded control signal and instead "
            "models external feedback behavior."
        )
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing *_control_rows.csv, *_feedback_rows.csv, and control_feedback_overlay.csv.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for derived CSV/JSON outputs. Default: <input_dir>/v22_out",
    )
    parser.add_argument(
        "--feedback-signal",
        default="s16be_b6_7",
        help="Feedback signal to analyze. Default: s16be_b6_7",
    )
    parser.add_argument(
        "--min-group-size",
        type=int,
        default=50,
        help="Minimum rows required for grouped regression. Default: 50",
    )
    parser.add_argument(
        "--deadband-control-bin",
        type=float,
        default=100.0,
        help="Absolute-control bin width for deadband summary. Default: 100",
    )
    parser.add_argument(
        "--deadband-feedback-step-threshold",
        type=float,
        default=2.0,
        help="Step threshold considered 'near static' for feedback. Default: 2",
    )
    parser.add_argument(
        "--deadband-min-static-ratio",
        type=float,
        default=0.75,
        help="Minimum static ratio for a bin to be considered deadband-like. Default: 0.75",
    )
    parser.add_argument(
        "--deadband-min-bin-count",
        type=int,
        default=25,
        help="Minimum sample count for a bin to participate in deadband inference. Default: 25",
    )
    parser.add_argument(
        "--arx-control-lags",
        type=int,
        default=5,
        help="Number of control lags for ARX-style model. Default: 5",
    )
    parser.add_argument(
        "--arx-feedback-lags",
        type=int,
        default=2,
        help="Number of feedback lags for ARX-style model. Default: 2",
    )
    parser.add_argument(
        "--control-index-min",
        type=int,
        default=None,
        help="Keep only rows with control_index >= this value.",
    )
    parser.add_argument(
        "--control-index-max",
        type=int,
        default=None,
        help="Keep only rows with control_index <= this value.",
    )
    parser.add_argument(
        "--domain",
        action="append",
        default=None,
        help="Keep only rows whose domain matches this value. Repeatable.",
    )
    parser.add_argument(
        "--b5-s8",
        action="append",
        type=int,
        default=None,
        help="Keep only rows whose b5_s8 matches this value. Repeatable.",
    )
    parser.add_argument(
        "--b1",
        action="append",
        type=int,
        default=None,
        help="Keep only rows whose b1 matches this value. Repeatable.",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="Optional analysis label written into summary.json for band/regime tracking.",
    )
    parser.add_argument(
        "--max-join-delta-ms",
        type=int,
        default=25,
        help="Maximum timestamp delta for overlay fallback rebuild. Default: 25",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def to_int(value: str) -> int:
    return int(float(value))


def to_float(value: str) -> float:
    return float(value)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def variance(values: list[float]) -> float:
    if not values:
        return 0.0
    mu = mean(values)
    return sum((v - mu) ** 2 for v in values) / len(values)


def stddev(values: list[float]) -> float:
    return math.sqrt(variance(values))


def covariance(xs: list[float], ys: list[float]) -> float:
    mu_x = mean(xs)
    mu_y = mean(ys)
    return sum((x - mu_x) * (y - mu_y) for x, y in zip(xs, ys)) / len(xs)


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    low = int(math.floor(pos))
    high = int(math.ceil(pos))
    if low == high:
        return ordered[low]
    frac = pos - low
    return ordered[low] * (1.0 - frac) + ordered[high] * frac


def simple_regression(xs: list[float], ys: list[float]) -> dict:
    mu_x = mean(xs)
    mu_y = mean(ys)
    var_x = variance(xs)
    if var_x == 0:
        slope = 0.0
        intercept = mu_y
    else:
        slope = covariance(xs, ys) / var_x
        intercept = mu_y - slope * mu_x
    preds = [slope * x + intercept for x in xs]
    residuals = [y - pred for y, pred in zip(ys, preds)]
    ss_tot = sum((y - mu_y) ** 2 for y in ys)
    ss_res = sum(r * r for r in residuals)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    corr_den = math.sqrt(variance(xs) * variance(ys))
    corr = covariance(xs, ys) / corr_den if corr_den > 0 else 0.0
    mae = mean([abs(r) for r in residuals])
    return {
        "slope": slope,
        "intercept": intercept,
        "r2": r2,
        "corr": corr,
        "mae": mae,
    }


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    out = [[0.0 for _ in range(len(b[0]))] for _ in range(len(a))]
    for i in range(len(a)):
        for k in range(len(b)):
            aik = a[i][k]
            for j in range(len(b[0])):
                out[i][j] += aik * b[k][j]
    return out


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*matrix)]


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(a)
    aug = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("Singular matrix in regression solve")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        pivot_val = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] /= pivot_val
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            for j in range(col, n + 1):
                aug[row][j] -= factor * aug[col][j]
    return [aug[i][n] for i in range(n)]


def multiple_regression(feature_names: list[str], rows: list[dict], target_key: str) -> dict:
    x_rows: list[list[float]] = []
    y_vals: list[float] = []
    for row in rows:
        x_rows.append([1.0] + [float(row[name]) for name in feature_names])
        y_vals.append(float(row[target_key]))
    xt = transpose(x_rows)
    xtx = matmul(xt, x_rows)
    xty_mat = matmul(xt, [[y] for y in y_vals])
    xty = [cell[0] for cell in xty_mat]
    coeffs = solve_linear_system(xtx, xty)
    preds = [sum(c * x for c, x in zip(coeffs, xs)) for xs in x_rows]
    mu_y = mean(y_vals)
    residuals = [y - pred for y, pred in zip(y_vals, preds)]
    ss_tot = sum((y - mu_y) ** 2 for y in y_vals)
    ss_res = sum(r * r for r in residuals)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    mae = mean([abs(r) for r in residuals])
    coeff_map = {"intercept": coeffs[0]}
    for idx, name in enumerate(feature_names, start=1):
        coeff_map[name] = coeffs[idx]
    return {
        "coefficients": coeff_map,
        "r2": r2,
        "mae": mae,
        "count": len(rows),
    }


def find_single_file(input_dir: Path, suffix: str) -> Path:
    matches = sorted(input_dir.glob(suffix))
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected exactly one match for {suffix}, found {len(matches)}")
    return matches[0]


def zscore(values: list[float]) -> list[float]:
    if not values:
        return []
    mu = mean(values)
    sd = stddev(values)
    if sd == 0:
        return [0.0 for _ in values]
    return [(v - mu) / sd for v in values]


def nearest_join_rows(control_rows: list[dict], feedback_rows: list[dict], max_delta_ms: int) -> list[dict]:
    out: list[dict] = []
    if not feedback_rows:
        return out
    j = 0
    for cr in control_rows:
        best = None
        while (
            j + 1 < len(feedback_rows)
            and abs(to_int(feedback_rows[j + 1]["ts_ms"]) - to_int(cr["ts_ms"]))
            <= abs(to_int(feedback_rows[j]["ts_ms"]) - to_int(cr["ts_ms"]))
        ):
            j += 1
        for k in (j - 1, j, j + 1):
            if 0 <= k < len(feedback_rows):
                d = abs(to_int(feedback_rows[k]["ts_ms"]) - to_int(cr["ts_ms"]))
                if best is None or d < best[0]:
                    best = (d, feedback_rows[k])
        if best is None or best[0] > max_delta_ms:
            continue
        feedback_row = best[1]
        joined = {
            "control_index": to_int(cr["index"]),
            "control_ts_s": to_float(cr["ts_s"]),
            "control": to_float(cr["control"]),
            "feedback_index": to_int(feedback_row["index"]),
            "feedback_ts_s": to_float(feedback_row["ts_s"]),
            "feedback_delta_ms": best[0],
        }
        for key, value in feedback_row.items():
            if key not in {"index", "ts_ms", "ts_s", "raw"}:
                joined[key] = value
        out.append(joined)
    return out


def aligned_overlay_rows(join_rows: list[dict], signal: str, lag: int) -> list[dict]:
    control = [float(r["control"]) for r in join_rows]
    feedback = [float(r[signal]) for r in join_rows]
    if lag > 0:
        control2, feedback2, base_rows = control[:-lag], feedback[lag:], join_rows[:-lag]
    elif lag < 0:
        control2, feedback2, base_rows = control[-lag:], feedback[:lag], join_rows[-lag:]
    else:
        control2, feedback2, base_rows = control, feedback, join_rows
    zc = zscore(control2)
    zf = zscore(feedback2)
    out = []
    for i, br in enumerate(base_rows):
        out.append(
            {
                "control_index": br["control_index"],
                "control_ts_s": br["control_ts_s"],
                "control": control2[i],
                "feedback_signal": signal,
                "feedback_value": feedback2[i],
                "control_z": zc[i],
                "feedback_z": zf[i],
            }
        )
    return out


def rebuild_overlay_rows(
    input_dir: Path,
    control_rows: list[dict],
    feedback_signal: str,
    max_join_delta_ms: int,
) -> tuple[list[dict], str | None, int | None]:
    feedback_rows_path = find_single_file(input_dir, "*_feedback_rows.csv")
    lag_scores_path = find_single_file(input_dir, "*_lag_scores.csv")
    feedback_rows = read_csv(feedback_rows_path)
    lag_rows = read_csv(lag_scores_path)
    lag_match = next((row for row in lag_rows if row["signal"] == feedback_signal), None)
    if lag_match is None:
        return [], None, None
    lag = to_int(lag_match["best_lag_frames"])
    join_rows = nearest_join_rows(control_rows, feedback_rows, max_delta_ms=max_join_delta_ms)
    if not join_rows:
        return [], feedback_signal, lag
    if feedback_signal not in join_rows[0]:
        return [], feedback_signal, lag
    return aligned_overlay_rows(join_rows, feedback_signal, lag), feedback_signal, lag


def build_aligned_rows(
    input_dir: Path,
    feedback_signal: str,
    max_join_delta_ms: int,
) -> tuple[list[dict], str, int | None]:
    control_rows_path = find_single_file(input_dir, "*_control_rows.csv")
    control_rows = read_csv(control_rows_path)
    overlay_rows = []
    overlay_source = "existing_overlay"
    resolved_lag = None
    overlay_path = input_dir / "control_feedback_overlay.csv"
    if overlay_path.exists():
        overlay_rows = [row for row in read_csv(overlay_path) if row["feedback_signal"] == feedback_signal]
    if not overlay_rows:
        overlay_rows, _, resolved_lag = rebuild_overlay_rows(
            input_dir=input_dir,
            control_rows=control_rows,
            feedback_signal=feedback_signal,
            max_join_delta_ms=max_join_delta_ms,
        )
        overlay_source = "rebuilt_from_feedback_rows"
    by_index = {to_int(row["index"]): row for row in control_rows}
    aligned: list[dict] = []
    for overlay in overlay_rows:
        idx = to_int(overlay["control_index"])
        control_row = by_index.get(idx)
        if control_row is None:
            continue
        aligned.append(
            {
                "control_index": idx,
                "control_ts_s": to_float(overlay["control_ts_s"]),
                "control": to_float(overlay["control"]),
                "feedback_signal": overlay["feedback_signal"],
                "feedback_value": to_float(overlay["feedback_value"]),
                "b1": to_int(control_row["b1"]),
                "b5": to_int(control_row["b5"]),
                "b5_s8": to_int(control_row["b5_s8"]),
                "domain": control_row["domain"],
                "fine_term_b23": to_float(control_row["fine_term_b23"]),
                "coarse_term_b5": to_float(control_row["coarse_term_b5"]),
                "overlay_source": overlay_source,
            }
        )
    aligned.sort(key=lambda row: row["control_index"])
    return aligned, overlay_source, resolved_lag


def filter_aligned_rows(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    out = rows
    if args.control_index_min is not None:
        out = [row for row in out if int(row["control_index"]) >= args.control_index_min]
    if args.control_index_max is not None:
        out = [row for row in out if int(row["control_index"]) <= args.control_index_max]
    if args.domain:
        allowed = set(args.domain)
        out = [row for row in out if str(row["domain"]) in allowed]
    if args.b5_s8:
        allowed = set(args.b5_s8)
        out = [row for row in out if int(row["b5_s8"]) in allowed]
    if args.b1:
        allowed = set(args.b1)
        out = [row for row in out if int(row["b1"]) in allowed]
    return out


def grouped_feedback_regressions(
    rows: list[dict], group_key: str, min_group_size: int
) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[str(row[group_key])].append(row)
    results: list[dict] = []
    for group_value, group_rows in sorted(groups.items(), key=lambda item: item[0]):
        if len(group_rows) < min_group_size:
            continue
        xs = [float(row["control"]) for row in group_rows]
        ys = [float(row["feedback_value"]) for row in group_rows]
        fit = simple_regression(xs, ys)
        results.append(
            {
                "group_key": group_key,
                "group_value": group_value,
                "count": len(group_rows),
                "slope": fit["slope"],
                "intercept": fit["intercept"],
                "corr": fit["corr"],
                "r2": fit["r2"],
                "mae": fit["mae"],
                "control_min": min(xs),
                "control_max": max(xs),
                "feedback_min": min(ys),
                "feedback_max": max(ys),
            }
        )
    return results


def deadband_summary(
    rows: list[dict],
    control_bin: float,
    feedback_step_threshold: float,
    min_static_ratio: float,
    min_bin_count: int,
) -> tuple[list[dict], dict]:
    enriched: list[dict] = []
    prev_feedback = None
    for row in rows:
        row_copy = dict(row)
        if prev_feedback is None:
            row_copy["feedback_step_abs"] = 0.0
        else:
            row_copy["feedback_step_abs"] = abs(float(row["feedback_value"]) - prev_feedback)
        prev_feedback = float(row["feedback_value"])
        row_copy["abs_control"] = abs(float(row["control"]))
        bin_index = int(row_copy["abs_control"] // control_bin)
        row_copy["control_bin_lo"] = bin_index * control_bin
        row_copy["control_bin_hi"] = (bin_index + 1) * control_bin
        enriched.append(row_copy)

    bins: dict[tuple[float, float], list[dict]] = defaultdict(list)
    for row in enriched:
        bins[(row["control_bin_lo"], row["control_bin_hi"])].append(row)

    bin_rows: list[dict] = []
    likely_deadband_hi = None
    contiguous_mode = True
    for (lo, hi), group in sorted(bins.items()):
        steps = [float(item["feedback_step_abs"]) for item in group]
        static_count = sum(1 for step in steps if step <= feedback_step_threshold)
        static_ratio = static_count / len(group)
        qualified = (
            len(group) >= min_bin_count
            and static_ratio >= min_static_ratio
            and percentile(steps, 0.5) <= feedback_step_threshold
        )
        row = {
            "control_bin_lo": lo,
            "control_bin_hi": hi,
            "count": len(group),
            "mean_feedback_step_abs": mean(steps),
            "median_feedback_step_abs": percentile(steps, 0.5),
            "p90_feedback_step_abs": percentile(steps, 0.9),
            "static_ratio": static_ratio,
            "qualified_for_deadband": qualified,
        }
        bin_rows.append(row)
        if contiguous_mode and qualified:
            likely_deadband_hi = hi
        elif len(group) >= min_bin_count:
            contiguous_mode = False

    summary = {
        "feedback_step_threshold": feedback_step_threshold,
        "control_bin_width": control_bin,
        "min_bin_count": min_bin_count,
        "likely_deadband_abs_control_hi": likely_deadband_hi,
        "likely_deadband_range": (
            [-likely_deadband_hi, likely_deadband_hi] if likely_deadband_hi is not None else None
        ),
    }
    return bin_rows, summary


def regime_deadband_summaries(
    rows: list[dict],
    regime_key: str,
    control_bin: float,
    feedback_step_threshold: float,
    min_static_ratio: float,
    min_bin_count: int,
) -> tuple[list[dict], list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[str(row[regime_key])].append(row)

    all_bin_rows: list[dict] = []
    summary_rows: list[dict] = []
    for regime_value, regime_rows in sorted(grouped.items(), key=lambda item: item[0]):
        bin_rows, summary = deadband_summary(
            regime_rows,
            control_bin=control_bin,
            feedback_step_threshold=feedback_step_threshold,
            min_static_ratio=min_static_ratio,
            min_bin_count=min_bin_count,
        )
        for row in bin_rows:
            row_copy = dict(row)
            row_copy["regime_key"] = regime_key
            row_copy["regime_value"] = regime_value
            all_bin_rows.append(row_copy)
        summary_rows.append(
            {
                "regime_key": regime_key,
                "regime_value": regime_value,
                "count": len(regime_rows),
                "likely_deadband_abs_control_hi": summary["likely_deadband_abs_control_hi"],
                "likely_deadband_range": json.dumps(summary["likely_deadband_range"]),
            }
        )
    return all_bin_rows, summary_rows


def arx_rows(rows: list[dict], control_lags: int, feedback_lags: int) -> list[dict]:
    out: list[dict] = []
    start = max(control_lags - 1, feedback_lags)
    for idx in range(start, len(rows)):
        row: dict[str, float] = {
            "y_feedback": float(rows[idx]["feedback_value"]),
        }
        for lag in range(control_lags):
            row[f"control_lag_{lag}"] = float(rows[idx - lag]["control"])
        for lag in range(1, feedback_lags + 1):
            row[f"feedback_lag_{lag}"] = float(rows[idx - lag]["feedback_value"])
        out.append(row)
    return out


def ar_rows(rows: list[dict], feedback_lags: int) -> list[dict]:
    out: list[dict] = []
    start = feedback_lags
    for idx in range(start, len(rows)):
        row: dict[str, float] = {
            "y_feedback": float(rows[idx]["feedback_value"]),
        }
        for lag in range(1, feedback_lags + 1):
            row[f"feedback_lag_{lag}"] = float(rows[idx - lag]["feedback_value"])
        out.append(row)
    return out


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir / "v22_out"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_aligned_rows, overlay_source, resolved_lag = build_aligned_rows(
        input_dir, args.feedback_signal, args.max_join_delta_ms
    )
    aligned_rows = filter_aligned_rows(all_aligned_rows, args)
    if not aligned_rows:
        raise SystemExit(f"No aligned rows found for feedback signal {args.feedback_signal}")

    write_csv(
        output_dir / "aligned_feedback_rows.csv",
        aligned_rows,
        [
            "control_index",
            "control_ts_s",
            "control",
            "feedback_signal",
            "feedback_value",
            "b1",
            "b5",
            "b5_s8",
            "domain",
            "fine_term_b23",
            "coarse_term_b5",
            "overlay_source",
        ],
    )

    grouped_rows: list[dict] = []
    for key in ("b5_s8", "b1", "domain"):
        grouped_rows.extend(grouped_feedback_regressions(aligned_rows, key, args.min_group_size))
    write_csv(
        output_dir / "state_conditioned_feedback_regression.csv",
        grouped_rows,
        [
            "group_key",
            "group_value",
            "count",
            "slope",
            "intercept",
            "corr",
            "r2",
            "mae",
            "control_min",
            "control_max",
            "feedback_min",
            "feedback_max",
        ],
    )

    deadband_rows, deadband_info = deadband_summary(
        aligned_rows,
        control_bin=args.deadband_control_bin,
        feedback_step_threshold=args.deadband_feedback_step_threshold,
        min_static_ratio=args.deadband_min_static_ratio,
        min_bin_count=args.deadband_min_bin_count,
    )
    write_csv(
        output_dir / "feedback_deadband_bins.csv",
        deadband_rows,
        [
            "control_bin_lo",
            "control_bin_hi",
            "count",
            "mean_feedback_step_abs",
            "median_feedback_step_abs",
            "p90_feedback_step_abs",
            "static_ratio",
            "qualified_for_deadband",
        ],
    )

    regime_bin_rows_b5, regime_summary_b5 = regime_deadband_summaries(
        aligned_rows,
        regime_key="b5_s8",
        control_bin=args.deadband_control_bin,
        feedback_step_threshold=args.deadband_feedback_step_threshold,
        min_static_ratio=args.deadband_min_static_ratio,
        min_bin_count=args.deadband_min_bin_count,
    )
    regime_bin_rows_domain, regime_summary_domain = regime_deadband_summaries(
        aligned_rows,
        regime_key="domain",
        control_bin=args.deadband_control_bin,
        feedback_step_threshold=args.deadband_feedback_step_threshold,
        min_static_ratio=args.deadband_min_static_ratio,
        min_bin_count=args.deadband_min_bin_count,
    )
    write_csv(
        output_dir / "feedback_deadband_bins_by_regime.csv",
        regime_bin_rows_b5 + regime_bin_rows_domain,
        [
            "regime_key",
            "regime_value",
            "control_bin_lo",
            "control_bin_hi",
            "count",
            "mean_feedback_step_abs",
            "median_feedback_step_abs",
            "p90_feedback_step_abs",
            "static_ratio",
            "qualified_for_deadband",
        ],
    )
    write_csv(
        output_dir / "feedback_deadband_regime_summary.csv",
        regime_summary_b5 + regime_summary_domain,
        [
            "regime_key",
            "regime_value",
            "count",
            "likely_deadband_abs_control_hi",
            "likely_deadband_range",
        ],
    )

    arx_dataset = arx_rows(aligned_rows, args.arx_control_lags, args.arx_feedback_lags)
    arx_feature_names = [
        *[f"control_lag_{lag}" for lag in range(args.arx_control_lags)],
        *[f"feedback_lag_{lag}" for lag in range(1, args.arx_feedback_lags + 1)],
    ]
    ar_dataset = ar_rows(aligned_rows, args.arx_feedback_lags)
    ar_feature_names = [f"feedback_lag_{lag}" for lag in range(1, args.arx_feedback_lags + 1)]
    ar_fit = None
    ar_error = None
    if ar_dataset:
        try:
            ar_fit = multiple_regression(ar_feature_names, ar_dataset, "y_feedback")
        except ValueError as exc:
            ar_error = str(exc)
    else:
        ar_error = "Not enough aligned rows for AR dataset"

    ar_coeff_rows = []
    if ar_fit is not None:
        ar_coeff_rows = [{"term": name, "coefficient": value} for name, value in ar_fit["coefficients"].items()]
    write_csv(output_dir / "feedback_ar_baseline_coefficients.csv", ar_coeff_rows, ["term", "coefficient"])

    arx_fit = None
    arx_error = None
    if arx_dataset:
        try:
            arx_fit = multiple_regression(arx_feature_names, arx_dataset, "y_feedback")
        except ValueError as exc:
            arx_error = str(exc)
    else:
        arx_error = "Not enough aligned rows for ARX dataset"

    arx_coeff_rows = []
    if arx_fit is not None:
        arx_coeff_rows = [
            {"term": name, "coefficient": value}
            for name, value in arx_fit["coefficients"].items()
        ]
    write_csv(output_dir / "feedback_arx_coefficients.csv", arx_coeff_rows, ["term", "coefficient"])

    model_comparison_rows = [
        {
            "model": "ar_feedback_only",
            "count": ar_fit["count"] if ar_fit is not None else 0,
            "r2": ar_fit["r2"] if ar_fit is not None else None,
            "mae": ar_fit["mae"] if ar_fit is not None else None,
            "error": ar_error,
        },
        {
            "model": "arx_feedback_plus_control",
            "count": arx_fit["count"] if arx_fit is not None else 0,
            "r2": arx_fit["r2"] if arx_fit is not None else None,
            "mae": arx_fit["mae"] if arx_fit is not None else None,
            "error": arx_error,
        },
    ]
    write_csv(output_dir / "feedback_model_comparison.csv", model_comparison_rows, ["model", "count", "r2", "mae", "error"])

    summary = {
        "input_dir": str(input_dir),
        "label": args.label,
        "feedback_signal": args.feedback_signal,
        "overlay_source": overlay_source,
        "resolved_feedback_lag": resolved_lag,
        "pre_filter_aligned_count": len(all_aligned_rows),
        "aligned_count": len(aligned_rows),
        "filters": {
            "control_index_min": args.control_index_min,
            "control_index_max": args.control_index_max,
            "domain": args.domain or [],
            "b5_s8": args.b5_s8 or [],
            "b1": args.b1 or [],
            "max_join_delta_ms": args.max_join_delta_ms,
        },
        "grouped_regression_groups": len(grouped_rows),
        "deadband": deadband_info,
        "regime_deadband_summary_rows": len(regime_summary_b5) + len(regime_summary_domain),
        "ar_baseline": {
            "feedback_lags": args.arx_feedback_lags,
            "count": ar_fit["count"] if ar_fit is not None else 0,
            "r2": ar_fit["r2"] if ar_fit is not None else None,
            "mae": ar_fit["mae"] if ar_fit is not None else None,
            "coefficients": ar_fit["coefficients"] if ar_fit is not None else {},
            "error": ar_error,
        },
        "arx": {
            "control_lags": args.arx_control_lags,
            "feedback_lags": args.arx_feedback_lags,
            "count": arx_fit["count"] if arx_fit is not None else 0,
            "r2": arx_fit["r2"] if arx_fit is not None else None,
            "mae": arx_fit["mae"] if arx_fit is not None else None,
            "coefficients": arx_fit["coefficients"] if arx_fit is not None else {},
            "error": arx_error,
        },
        "arx_gain_over_ar": {
            "r2_gain": (
                arx_fit["r2"] - ar_fit["r2"]
                if arx_fit is not None and ar_fit is not None
                else None
            ),
            "mae_reduction": (
                ar_fit["mae"] - arx_fit["mae"]
                if arx_fit is not None and ar_fit is not None
                else None
            ),
        },
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print(f"Wrote outputs to: {output_dir}")
    print(f"Aligned rows: {len(aligned_rows)}")
    print(f"Feedback signal: {args.feedback_signal}")
    print(f"Likely deadband range: {deadband_info['likely_deadband_range']}")
    if ar_fit is not None:
        print(f"AR baseline R2: {ar_fit['r2']:.6f}")
        print(f"AR baseline MAE: {ar_fit['mae']:.6f}")
    else:
        print(f"AR baseline skipped: {ar_error}", file=sys.stderr)
    if arx_fit is not None:
        print(f"ARX R2: {arx_fit['r2']:.6f}")
        print(f"ARX MAE: {arx_fit['mae']:.6f}")
        if ar_fit is not None:
            print(f"ARX R2 gain over AR: {arx_fit['r2'] - ar_fit['r2']:.6f}")
            print(f"ARX MAE reduction over AR: {ar_fit['mae'] - arx_fit['mae']:.6f}")
    else:
        print(f"ARX skipped: {arx_error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
