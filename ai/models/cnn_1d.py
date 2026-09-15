import numpy as np
import time
from pathlib import Path

# Framework independent design: training requires torch, inference relies purely on ONNX.
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

if TORCH_AVAILABLE:
    class CNN1DNet(nn.Module):
        def __init__(self, in_channels, num_classes):
            super().__init__()
            # Input shape: (batch, in_channels, 128)
            # Lightweight architecture specifically for Edge CPU
            self.features = nn.Sequential(
                nn.BatchNorm1d(in_channels),                                    # CRIT-1: Channel normalisation
                nn.Conv1d(in_channels, 16, kernel_size=5, stride=2, padding=2), # output length: 64
                nn.ReLU(),
                nn.Conv1d(16, 32, kernel_size=5, stride=2, padding=2),          # output length: 32
                nn.ReLU(),
                nn.Conv1d(32, 64, kernel_size=3, stride=2, padding=1),          # output length: 16
                nn.ReLU(),
                nn.AdaptiveAvgPool1d(1)                                         # output length: 1
            )
            self.classifier = nn.Linear(64, num_classes)
            
        def forward(self, x):
            x = self.features(x)
            x = x.view(x.size(0), -1)
            x = self.classifier(x)
            return x

class TemporalCNNModel:
    def __init__(self, model_path: str = None, in_channels: int = 10, num_classes: int = 8):
        self.in_channels = in_channels
        self.num_classes = num_classes
        self.model_path = model_path
        self.is_trained = False
        self.ort_session = None
        self.model_pytorch = None
        
        self.classes = [
            'NORMAL', 'OVERHEATING', 'IMPACT_LIKE_EVENT', 'HIGH_VIBRATION',
            'OBSTACLE_APPROACH', 'SENSOR_STUCK', 'SENSOR_DROPOUT', 'MULTI_SENSOR_ANOMALY'
        ]
        
        self.feature_columns = [
            'dht_temp', 'dht_hum', 'mpu_acc_x', 'mpu_acc_y', 'mpu_acc_z',
            'mpu_gyro_x', 'mpu_gyro_y', 'mpu_gyro_z', 'ultra_dist', 'pir_motion'
        ]
        
        if self.model_path and Path(self.model_path).exists():
            onnx_path = Path(self.model_path) / "cnn_1d.onnx"
            if onnx_path.exists() and ONNX_AVAILABLE:
                self.load_onnx(onnx_path)

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray, epochs=15):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for training.")
            
        self.model_pytorch = CNN1DNet(self.in_channels, self.num_classes)
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model_pytorch.parameters(), lr=0.001)
        
        X_train_t = torch.tensor(X_train, dtype=torch.float32)
        y_train_t = torch.tensor(y_train, dtype=torch.long)
        X_val_t = torch.tensor(X_val, dtype=torch.float32)
        y_val_t = torch.tensor(y_val, dtype=torch.long)
        
        dataset = torch.utils.data.TensorDataset(X_train_t, y_train_t)
        loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
        
        print("Training Lightweight 1D CNN...")
        for ep in range(epochs):
            self.model_pytorch.train()
            total_loss = 0
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                out = self.model_pytorch(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
                
            # Validation
            self.model_pytorch.eval()
            with torch.no_grad():
                val_out = self.model_pytorch(X_val_t)
                val_loss = criterion(val_out, y_val_t).item()
                _, preds = torch.max(val_out, 1)
                acc = (preds == y_val_t).float().mean().item()
                
            print(f"Epoch {ep+1:02d}/{epochs} | Train Loss: {total_loss/len(loader):.4f} | Val Loss: {val_loss:.4f} | Val Acc: {acc:.4f}")
            
        self.is_trained = True

    def export_onnx(self, out_dir: str):
        if not self.is_trained or not TORCH_AVAILABLE:
            raise ValueError("Model must be trained with PyTorch before exporting to ONNX.")
            
        out_path = Path(out_dir) / "cnn_1d.onnx"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.model_pytorch.eval()
        dummy_input = torch.randn(1, self.in_channels, 128)
        
        torch.onnx.export(
            self.model_pytorch, 
            dummy_input, 
            str(out_path), 
            input_names=["input"], 
            output_names=["output"],
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
        )
        print(f"Exported to ONNX: {out_path}")
        
        params = sum(p.numel() for p in self.model_pytorch.parameters())
        size_kb = out_path.stat().st_size / 1024
        print(f"Model Parameters: {params}")
        print(f"Model Size: {size_kb:.2f} KB")

    def load_onnx(self, onnx_path: str):
        if not ONNX_AVAILABLE:
            raise RuntimeError("onnxruntime is required for inference.")
        # Setup onnxruntime to use CPU strictly
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 1
        self.ort_session = ort.InferenceSession(str(onnx_path), sess_options, providers=['CPUExecutionProvider'])
        self.is_trained = True
        
    def predict(self, window_df) -> dict:
        if not self.is_trained or self.ort_session is None:
            raise ValueError("Model is not loaded or trained. ONNX session required.")
            
        data = window_df[self.feature_columns].values
        data = np.nan_to_num(data) # Handle dropouts by zeroing out NaNs
        
        # Format for CNN: (batch=1, channels, seq_len=128)
        data = data.T 
        data = np.expand_dims(data, axis=0).astype(np.float32) 
        
        start_t = time.perf_counter()
        ort_inputs = {self.ort_session.get_inputs()[0].name: data}
        logits = self.ort_session.run(None, ort_inputs)[0][0]
        end_t = time.perf_counter()
        
        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / exp_logits.sum()
        
        pred_idx = int(np.argmax(probs))
        
        return {
            'predicted_class': self.classes[pred_idx],
            'confidence': float(probs[pred_idx]),
            'latency_ms': (end_t - start_t) * 1000.0,
            'class_probabilities': {self.classes[i]: float(probs[i]) for i in range(len(self.classes))},
            'metadata': {'model': 'CNN1D_ONNX'}
        }
