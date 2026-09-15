import xgboost as xgb
import numpy as np
import pandas as pd
from pathlib import Path
import joblib

class XGBoostFaultClassifier:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = xgb.XGBClassifier(
            max_depth=4,              # lightweight for RPi
            n_estimators=50,          # lightweight
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multi:softprob',
            eval_metric='mlogloss',
            random_state=42
        )
        self.is_trained = False
        self.version = "1.0.0"
        
        self.feature_names = [
            'acc_mag_mean', 'acc_mag_std', 'gyro_mag_mean', 'gyro_mag_std',
            'acc_x_var', 'acc_y_var', 'acc_z_var', 'vibration_zcr',
            'temp_roc', 'dist_roc', 'dht_valid', 'ultra_valid', 'mpu_valid'
        ]
        
        self.classes = [
            'NORMAL',
            'OVERHEATING',
            'IMPACT_LIKE_EVENT',
            'HIGH_VIBRATION',
            'OBSTACLE_APPROACH',
            'SENSOR_STUCK',
            'SENSOR_DROPOUT',
            'MULTI_SENSOR_ANOMALY'
        ]
        
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}
        
        if self.model_path and Path(self.model_path).exists():
            if (Path(self.model_path) / 'xgb_model.json').exists():
                self.load(self.model_path)

    def _extract_feature_array(self, features_dict: dict) -> np.ndarray:
        return np.array([[features_dict.get(k, 0.0) for k in self.feature_names]])

    def fit(self, features_df: pd.DataFrame, labels: pd.Series, eval_set=None):
        X = features_df[self.feature_names].values
        X = np.nan_to_num(X)
        
        y = np.array([self.class_to_idx[lbl] for lbl in labels])
        
        eval_data = None
        if eval_set:
            X_val, y_val_str = eval_set
            X_val = X_val[self.feature_names].values
            X_val = np.nan_to_num(X_val)
            y_val = np.array([self.class_to_idx[lbl] for lbl in y_val_str])
            eval_data = [(X, y), (X_val, y_val)]
            
        self.model.fit(
            X, y,
            eval_set=eval_data,
            verbose=False
        )
        self.is_trained = True

    def predict(self, features_dict: dict) -> dict:
        if not self.is_trained:
            raise ValueError("Model is not trained.")
            
        X = self._extract_feature_array(features_dict)
        X = np.nan_to_num(X)
        
        # XGBoost predict_proba outputs (1, n_classes)
        probs = self.model.predict_proba(X)[0]
        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        
        predicted_class = self.classes[pred_idx]
        
        class_probs = {self.classes[i]: float(probs[i]) for i in range(len(self.classes))}
        
        return {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'class_probabilities': class_probs,
            'metadata': {
                'model': 'XGBoost',
                'version': self.version
            }
        }

    def save(self, directory: str):
        if not self.is_trained:
            raise ValueError("Cannot save untrained model.")
        out_dir = Path(directory)
        out_dir.mkdir(parents=True, exist_ok=True)
        self.model.save_model(out_dir / 'xgb_model.json')
        self.model_path = str(out_dir)

    def load(self, directory: str):
        in_dir = Path(directory)
        self.model.load_model(in_dir / 'xgb_model.json')
        self.is_trained = True
