#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path


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


def corr(xs: list[float], ys: list[float]) -> float | None:
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


def analyze_session(base: Path, files: list[str]) -> dict:
    rows: list[tuple[int, int, list[int]]] = []
    for name in files:
        with (base / name).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if row.get("bus") != 0:
                    continue
                if row.get("addr") not in (0x260, 0x191):
                    continue
                rows.append((row["ts_ms"], row["addr"], parse_hex(row["data"])))
    rows.sort()
    control: list[float] = []
    b45: list[float] = []
    b67: list[float] = []
    last_191: tuple[int, int, int] | None = None
    for ts, addr, buf in rows:
        if addr == 0x191:
            last_191 = (ts, s16le(buf, 4), s16be(buf, 6))
            continue
        if last_191 is None or abs(ts - last_191[0]) > 100:
            continue
        control.append(float(control_from_260(buf)))
        b45.append(float(last_191[1]))
        b67.append(float(last_191[2]))
    c45 = corr(control, b45)
    c67 = corr(control, b67)
    pref = "insufficient"
    if c45 is not None and c67 is not None:
        if abs(c45) > abs(c67) + 0.05:
            pref = "b4-b5"
        elif abs(c67) > abs(c45) + 0.05:
            pref = "b6-b7"
        else:
            pref = "near-dual-field"
    return {
        "pairs": len(control),
        "corr_b45": None if c45 is None else round(c45, 3),
        "corr_b67": None if c67 is None else round(c67, 3),
        "abs_b45": None if c45 is None else round(abs(c45), 3),
        "abs_b67": None if c67 is None else round(abs(c67), 3),
        "preference": pref,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize 0x191 companion-field preference for grouped sessions.")
    parser.add_argument("--base", required=True, help="Directory containing NDJSON files")
    parser.add_argument(
        "--session",
        action="append",
        required=True,
        help="Format: session_name=file1,file2,file3",
    )
    args = parser.parse_args()

    base = Path(args.base)
    out: dict[str, dict] = {}
    for spec in args.session:
        name, raw_files = spec.split("=", 1)
        files = [part for part in raw_files.split(",") if part]
        out[name] = analyze_session(base, files)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
