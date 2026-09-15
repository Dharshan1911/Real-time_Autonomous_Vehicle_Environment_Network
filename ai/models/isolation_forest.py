import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from pathlib import Path

class IsolationForestModel:
    def __init__(self, contamination="auto", model_path: str = None):
        self.contamination = contamination
        self.model_path = model_path
        # Use random_state for reproducibility
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
        self.scaler = StandardScaler()
        self.empirical_threshold = -0.5 # Default fallback
        self.is_trained = False
        self.version = "1.0.0"
        
        # Features expected by this model (order matters)
        self.feature_names = [
            'acc_mag_mean', 'acc_mag_std', 'gyro_mag_mean', 'gyro_mag_std',
            'acc_x_var', 'acc_y_var', 'acc_z_var', 'vibration_zcr',
            'temp_roc', 'dist_roc', 'dht_valid', 'ultra_valid', 'mpu_valid'
        ]
        
        if self.model_path and Path(self.model_path).exists():
            # If path is provided, try loading
            if (Path(self.model_path) / 'iso_forest.joblib').exists():
                self.load(self.model_path)

    def _extract_feature_array(self, features_dict: dict) -> np.ndarray:
        return np.array([[features_dict.get(k, 0.0) for k in self.feature_names]])

    def fit(self, features_df: pd.DataFrame):
        # Extract only the needed features, handle any NaNs robustly
        X = features_df[self.feature_names].values
        X = np.nan_to_num(X) 
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True

    def predict(self, features_dict: dict) -> dict:
        if not self.is_trained:
            raise ValueError("Model is not trained.")
        
        X = self._extract_feature_array(features_dict)
        X = np.nan_to_num(X)
        X_scaled = self.scaler.transform(X)
        
        # score_samples returns negative anomaly score. Lower -> more abnormal.
        score = self.model.score_samples(X_scaled)[0]
        
        # CRIT-2: Use empirical threshold instead of sklearn's default
        is_anomaly = bool(score < self.empirical_threshold)
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': float(score),
            'metadata': {
                'model': 'IsolationForest',
                'version': self.version,
                'contamination_setting': self.contamination,
                'empirical_threshold': self.empirical_threshold
            }
        }

    def save(self, directory: str):
        if not self.is_trained:
            raise ValueError("Cannot save untrained model.")
        out_dir = Path(directory)
        out_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, out_dir / 'iso_forest.joblib')
        joblib.dump(self.scaler, out_dir / 'iso_scaler.joblib')
        joblib.dump(self.empirical_threshold, out_dir / 'iso_threshold.joblib')
        self.model_path = str(out_dir)

    def load(self, directory: str):
        in_dir = Path(directory)
        self.model = joblib.load(in_dir / 'iso_forest.joblib')
        self.scaler = joblib.load(in_dir / 'iso_scaler.joblib')
        
        threshold_path = in_dir / 'iso_threshold.joblib'
        if threshold_path.exists():
            self.empirical_threshold = joblib.load(threshold_path)
            
        self.is_trained = True
