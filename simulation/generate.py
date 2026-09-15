import argparse
from pathlib import Path
from simulation.engine import SyntheticTelemetryEngine
import os

def main():
    parser = argparse.ArgumentParser(description="RAVEN Synthetic Telemetry Engine")
    parser.add_argument('--scenario', type=str, required=True, 
                        help="Scenario to generate (e.g., NORMAL, OVERHEATING, etc.) or 'ALL'")
    parser.add_argument('--duration', type=float, default=10.0, help="Duration in seconds")
    parser.add_argument('--fps', type=int, default=50, help="Sampling frequency")
    parser.add_argument('--seed', type=int, default=42, help="Random seed")
    parser.add_argument('--noise', type=float, default=1.0, help="Noise multiplier")
    parser.add_argument('--fault_start', type=float, default=0.3, help="Fraction of duration when fault starts")
    parser.add_argument('--fault_end', type=float, default=0.7, help="Fraction of duration when fault ends")
    parser.add_argument('--output_dir', type=str, default="data/synthetic", help="Output directory")

    args = parser.parse_args()

    scenarios = [
        'NORMAL', 'OVERHEATING', 'SUDDEN_ACCELERATION', 'IMPACT_LIKE_EVENT',
        'HIGH_VIBRATION', 'OBSTACLE_APPROACH', 'PIR_ACTIVITY', 'SENSOR_STUCK',
        'SENSOR_NOISE', 'SENSOR_DROPOUT', 'MULTI_SENSOR_ANOMALY'
    ]

    target_scenarios = scenarios if args.scenario == 'ALL' else [args.scenario]

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    engine = SyntheticTelemetryEngine(
        fps=args.fps, 
        duration=args.duration, 
        seed=args.seed,
        noise_level=args.noise
    )

    for sc in target_scenarios:
        if sc not in scenarios:
            print(f"Skipping unknown scenario: {sc}")
            continue
            
        print(f"Generating {sc}...")
        df = engine.generate(sc, fault_start=args.fault_start, fault_end=args.fault_end)
        
        # Save to CSV
        file_path = out_dir / f"{sc.lower()}_seed{args.seed}.csv"
        df.to_csv(file_path, index=False)
        print(f"Saved {len(df)} samples to {file_path}")

if __name__ == "__main__":
    main()
