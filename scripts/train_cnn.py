import os
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.paths import SYNTHETIC_DATA_DIR, MODELS_DIR
from ai.models.cnn_1d import TemporalCNNModel

def build_temporal_dataset(seed: int, target_classes: list, window_size=128, stride=64):
    feature_columns = [
        'dht_temp', 'dht_hum', 'mpu_acc_x', 'mpu_acc_y', 'mpu_acc_z',
        'mpu_gyro_x', 'mpu_gyro_y', 'mpu_gyro_z', 'ultra_dist', 'pir_motion'
    ]
    
    X_list = []
    y_list = []
    class_to_idx = {cls: i for i, cls in enumerate(target_classes)}
    
    for cls in target_classes:
        filename = f"{cls.lower()}_seed{seed}.csv"
        filepath = SYNTHETIC_DATA_DIR / filename
        if not filepath.exists():
            continue
            
        df = pd.read_csv(filepath)
        for start in range(0, len(df) - window_size + 1, stride):
            w = df.iloc[start:start+window_size]
            
            unique_labels = w['label'].unique()
            if cls in unique_labels:
                true_label = cls
            else:
                true_label = w['label'].iloc[-1]
                
            if true_label in target_classes:
                data = w[feature_columns].values
                data = np.nan_to_num(data)
                # Ensure input is scaled properly (basic standardization for CNN)
                # A proper implementation would use a fitted Scaler, but for now we standard scale per-channel roughly
                
                # Format: (channels, seq_len)
                data = data.T
                X_list.append(data)
                y_list.append(class_to_idx[true_label])
                
    if not X_list:
        return np.array([]), np.array([])
    return np.stack(X_list), np.array(y_list)

def main():
    model = TemporalCNNModel(in_channels=10, num_classes=8)
    target_classes = model.classes
    
    print("Building temporal datasets...")
    X_train, y_train = build_temporal_dataset(101, target_classes, stride=128)
    X_val, y_val = build_temporal_dataset(102, target_classes, stride=128)
    X_test, y_test = build_temporal_dataset(103, target_classes, stride=128)
    
    print(f"Train size: {len(X_train)}, Val size: {len(X_val)}, Test size: {len(X_test)}")
    
    if len(X_train) == 0:
        print("No training data found.")
        return
        
    model.fit(X_train, y_train, X_val, y_val, epochs=20)
    
    model.export_onnx(MODELS_DIR)
    
    # Reload purely via ONNX for validation
    model.load_onnx(Path(MODELS_DIR) / "cnn_1d.onnx")
    
    print("\n--- CNN ONNX Evaluation on Test Set ---")
    y_pred = []
    y_true = []
    latencies = []
    
    test_seed = 103
    for cls in target_classes:
        filepath = SYNTHETIC_DATA_DIR / f"{cls.lower()}_seed{test_seed}.csv"
        if not filepath.exists():
            continue
        df = pd.read_csv(filepath)
        for start in range(0, len(df) - 128 + 1, 128):
            w = df.iloc[start:start+128]
            
            unique_labels = w['label'].unique()
            true_label = cls if cls in unique_labels else w['label'].iloc[-1]
            
            if true_label in target_classes:
                pred = model.predict(w)
                y_pred.append(pred['predicted_class'])
                y_true.append(true_label)
                latencies.append(pred['latency_ms'])
                
    print(classification_report(y_true, y_pred, labels=target_classes, zero_division=0))
    print(f"Average Inference Latency (Host CPU): {sum(latencies)/len(latencies):.2f} ms")

if __name__ == "__main__":
    main()
