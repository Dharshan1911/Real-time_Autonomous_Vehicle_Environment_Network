import numpy as np
import pandas as pd

class FeatureExtractor:
    def __init__(self, fps: int = 50):
        self.fps = fps
        self.dt = 1.0 / fps
        
    def extract(self, df: pd.DataFrame) -> dict:
        """
        Extracts tabular features from a temporal window (DataFrame).
        Returns a dictionary of single scalar features representing the window.
        """
        features = {}
        
        # 1. Acceleration and Gyro Magnitudes
        acc_mag = np.sqrt(df['mpu_acc_x']**2 + df['mpu_acc_y']**2 + df['mpu_acc_z']**2)
        gyro_mag = np.sqrt(df['mpu_gyro_x']**2 + df['mpu_gyro_y']**2 + df['mpu_gyro_z']**2)
        
        features['acc_mag_mean'] = acc_mag.mean()
        features['acc_mag_std'] = acc_mag.std()
        features['gyro_mag_mean'] = gyro_mag.mean()
        features['gyro_mag_std'] = gyro_mag.std()
        
        # 2. Rolling/Window Statistics
        features['acc_x_var'] = df['mpu_acc_x'].var()
        features['acc_y_var'] = df['mpu_acc_y'].var()
        features['acc_z_var'] = df['mpu_acc_z'].var()
        
        # 3. Vibration statistics (high frequency changes)
        centered_acc_z = df['mpu_acc_z'] - df['mpu_acc_z'].mean()
        # count zero crossings
        zero_crossings = np.where(np.diff(np.signbit(centered_acc_z)))[0]
        features['vibration_zcr'] = len(zero_crossings) / (len(df) * self.dt)
        
        # 4. Deltas (Rate of change)
        time_span = df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]
        if time_span == 0:
            time_span = self.dt
            
        features['delta_temp'] = df['dht_temp'].iloc[-1] - df['dht_temp'].iloc[0]
        features['temp_roc'] = features['delta_temp'] / time_span
        
        features['delta_dist'] = df['ultra_dist'].iloc[-1] - df['ultra_dist'].iloc[0]
        features['dist_roc'] = features['delta_dist'] / time_span
        
        # 5. Sensor validity indicators
        features['dht_valid'] = int(not df['dht_temp'].isna().any())
        features['ultra_valid'] = int(not df['ultra_dist'].isna().any())
        features['mpu_valid'] = int(not df['mpu_acc_x'].isna().any())
        
        return features
