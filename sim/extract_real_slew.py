import pandas as pd
import numpy as np
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    args = parser.parse_args()

    try:
        # Load CSV
        df = pd.read_csv(args.input)
        
        # The probe CSV has 's16le_b4_5' which is already cast to signed 16-bit
        if 's16le_b4_5' not in df.columns:
            print("Error: Column 's16le_b4_5' not found in CSV.")
            return

        # Use the signed column to avoid manual wrap-around logic if possible,
        # but we still need to calculate deltas and handle potential spikes.
        setpoints = df['s16le_b4_5'].values
        
        if len(setpoints) == 0:
            print("No data points found.")
            return

        # Calculate raw deltas
        deltas = np.diff(setpoints)
        abs_deltas = np.abs(deltas)
        
        # Slew Sanitization:
        # In a real steering system, we don't expect jumps of e.g., 30000 in 10ms.
        # We filter out deltas that are physically impossible (e.g., > 5000)
        # as these are likely noise or remaining wrap-around artifacts.
        PHYSICAL_LIMIT = 5000 
        sanitized_deltas = abs_deltas[abs_deltas < PHYSICAL_LIMIT]
        
        if len(sanitized_deltas) == 0:
            print("All deltas were filtered out as non-physical.")
            return

        max_delta = np.max(sanitized_deltas)
        avg_delta = np.mean(sanitized_deltas)
        std_delta = np.std(sanitized_deltas)
        
        print(f"Analyzed {len(setpoints)} frames of 0x260 from CSV")
        print(f"Filtered out {len(abs_deltas) - len(sanitized_deltas)} non-physical spikes (> {PHYSICAL_LIMIT})")
        print(f"Sanitized Max Delta (Slew): {max_delta}")
        print(f"Sanitized Avg Delta: {avg_delta:.2f}")
        print(f"Sanitized Std Dev: {std_delta:.2f}")
        print(f"Setpoint Range: [{np.min(setpoints)}, {np.max(setpoints)}]")

        # Save results for audit
        with open("/home/vance/ToyotaSienna2024OpenpilotAnalysis/sim/slew_analysis_report.txt", "w") as f:
            f.write(f"Input: {args.input}\n")
            f.write(f"Total Frames: {len(setpoints)}\n")
            f.write(f"Spikes Filtered: {len(abs_deltas) - len(sanitized_deltas)}\n")
            f.write(f"Max Sanitized Delta: {max_delta}\n")
            f.write(f"Avg Sanitized Delta: {avg_delta:.2f}\n")
            f.write(f"Std Dev: {std_delta:.2f}\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
