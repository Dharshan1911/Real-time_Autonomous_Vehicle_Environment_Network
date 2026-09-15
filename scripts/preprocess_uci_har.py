import numpy as np
import pandas as pd
from pathlib import Path
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.paths import EXTERNAL_DATA_DIR, PROCESSED_DATA_DIR

def load_inertial_signals(dataset_dir: Path, group: str):
    signals = [
        "body_acc_x", "body_acc_y", "body_acc_z",
        "body_gyro_x", "body_gyro_y", "body_gyro_z"
    ]
    data = []
    for signal in signals:
        filepath = dataset_dir / group / "Inertial Signals" / f"{signal}_{group}.txt"
        df = pd.read_csv(filepath, sep=r'\s+', header=None)
        data.append(df.values)
    # Stack along the last axis to get (num_samples, 128, 6)
    return np.dstack(data)

def main():
    print("Loading UCI-HAR dataset (Inertial Signals only)...")
    try:
        X_train = load_inertial_signals(EXTERNAL_DATA_DIR, "train")
        X_test = load_inertial_signals(EXTERNAL_DATA_DIR, "test")
        
        y_train = pd.read_csv(EXTERNAL_DATA_DIR / "train" / "y_train.txt", header=None).values.flatten()
        y_test = pd.read_csv(EXTERNAL_DATA_DIR / "test" / "y_test.txt", header=None).values.flatten()
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")
    
    # Standardization (fit on train, apply to test) to prevent data leakage
    mean = np.mean(X_train, axis=(0, 1))
    std = np.std(X_train, axis=(0, 1))
    std[std == 0] = 1.0
    
    X_train_norm = (X_train - mean) / std
    X_test_norm = (X_test - mean) / std
    
    out_dir = PROCESSED_DATA_DIR / "uci_har"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    np.save(out_dir / "X_train.npy", X_train_norm)
    np.save(out_dir / "X_test.npy", X_test_norm)
    np.save(out_dir / "y_train.npy", y_train)
    np.save(out_dir / "y_test.npy", y_test)
    np.save(out_dir / "channel_means.npy", mean)
    np.save(out_dir / "channel_stds.npy", std)
    
    print(f"Processed data saved to {out_dir}")

if __name__ == "__main__":
    main()
