#!/usr/bin/env python3
import json
import argparse
from pathlib import Path

ADDR_116 = 0x116
ADDR_131 = 0x131
ADDR_260 = 0x260
TOP_TIER_ZONE = "fff4"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to the .ndjson log file")
    args = parser.parse_args()

    frames_116 = []
    latest_131 = None
    latest_260 = None

    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
                addr = row.get("addr")
                ts = row.get("ts_ms")
                data = bytes.fromhex(row.get("data"))

                if addr == ADDR_131:
                    latest_131 = (ts, data[2:4].hex())
                elif addr == ADDR_260:
                    latest_260 = (ts, data[3:5].hex())
                elif addr == ADDR_116:
                    fam131 = latest_131[1] if latest_131 and ts - latest_131[0] <= 250 else None
                    fam260 = latest_260[1] if latest_260 and ts - latest_260[0] <= 250 else None
                    
                    if fam131 == TOP_TIER_ZONE and fam260 == TOP_TIER_ZONE:
                        frames_116.append({
                            "ts": ts,
                            "phase_hex": data[0:2].hex(),
                            "phase_sum": data[0] + data[1]
                        })
            except Exception:
                continue

    if not frames_116:
        print("No top-tier zone activity found.")
        return

    # Find seed (0000)
    seed_idx = next((i for i, f in enumerate(frames_116) if f["phase_hex"] == "0000"), None)
    
    if seed_idx is None:
        print("No seed (0000) found in top-tier zone.")
        return

    print(f"Seed found at {frames_116[seed_idx]['ts']} ms")
    
    # Analyze ramping after seed
    ramp_window = frames_116[seed_idx:]
    max_sum = -1
    peak_ts = None
    
    print("\n--- Ramping Sequence ---")
    for f in ramp_window:
        print(f"TS: {f['ts']} | Phase: {f['phase_hex']} | Sum: {f['phase_sum']}")
        if f["phase_sum"] > max_sum:
            max_sum = f["phase_sum"]
            peak_ts = f["ts"]

    print("\n--- Summary ---")
    print(f"Peak Phase Sum: {max_sum}")
    print(f"Peak TS: {peak_ts}")
    if max_sum >= 130:
        print("Result: SUCCESS - reached plateau (>= 130)")
    elif max_sum > 0:
        print(f"Result: PARTIAL RAMP - peaked at {max_sum}")
    else:
        print("Result: NO RAMP")

if __name__ == "__main__":
    main()
