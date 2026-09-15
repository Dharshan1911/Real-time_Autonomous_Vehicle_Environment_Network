import os
import sys
from pathlib import Path
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.paths import SYNTHETIC_DATA_DIR, MODELS_DIR
from ai.features import FeatureExtractor
from ai.models.isolation_forest import IsolationForestModel

def window_dataframe(df, window_size=128, stride=128): 
    # Non-overlapping windows for strict evaluation
    windows = []
    labels = []
    for start in range(0, len(df) - window_size + 1, stride):
        w = df.iloc[start:start+window_size]
        windows.append(w)
        labels.append(w['label'].iloc[-1])
    return windows, labels

def main():
    print("Loading Trained Isolation Forest...")
    model_dir = MODELS_DIR
    if not (model_dir / 'iso_forest.joblib').exists():
        print("Model not found. Run training script first.")
        return
        
    model = IsolationForestModel(model_path=model_dir)
    extractor = FeatureExtractor(fps=50)
    
    scenarios = [
        "normal", "overheating", "impact_like_event", "high_vibration", 
        "obstacle_approach", "sensor_stuck", "sensor_dropout", "multi_sensor_anomaly"
    ]
    
    print("\n--- Isolation Forest Evaluation ---")
    print(f"{'Scenario':<25} | {'Anomalous Windows Found':<25} | {'Normal Windows False Alarms':<25}")
    print("-" * 85)
    
    for sc in scenarios:
        filepath = SYNTHETIC_DATA_DIR / f"{sc}_seed200.csv"
        if not filepath.exists():
            continue
            
        df = pd.read_csv(filepath)
        windows, labels = window_dataframe(df, window_size=128, stride=128)
        
        if not windows:
            continue
            
        anom_true_pos = 0
        anom_total = 0
        norm_false_pos = 0
        norm_total = 0
        
        for w, true_label in zip(windows, labels):
            feats = extractor.extract(w)
            pred = model.predict(feats)
            
            is_anomaly = pred['is_anomaly']
            
            if true_label != 'NORMAL':
                anom_total += 1
                if is_anomaly:
                    anom_true_pos += 1
            else:
                norm_total += 1
                if is_anomaly:
                    norm_false_pos += 1
                    
        anom_pct = (anom_true_pos / max(1, anom_total)) * 100
        norm_pct = (norm_false_pos / max(1, norm_total)) * 100
        
        anom_str = f"{anom_true_pos}/{anom_total} ({anom_pct:.1f}%)" if anom_total > 0 else "N/A"
        norm_str = f"{norm_false_pos}/{norm_total} ({norm_pct:.1f}%)"
        
        print(f"{sc:<25} | {anom_str:<25} | {norm_str:<25}")

if __name__ == "__main__":
    main()
