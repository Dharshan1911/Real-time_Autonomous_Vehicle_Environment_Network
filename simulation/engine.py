import pandas as pd
import numpy as np

class SyntheticTelemetryEngine:
    def __init__(self, fps=50, duration=10, seed=42, noise_level=1.0):
        self.fps = fps
        self.duration = duration
        self.seed = seed
        self.noise_level = noise_level
        self.num_samples = int(fps * duration)
        np.random.seed(seed)
        
    def _generate_base(self):
        # Time axis
        t = np.linspace(0, self.duration, self.num_samples, endpoint=False)
        
        # Base signals with some nominal noise
        # DHT
        dht_temp = np.full(self.num_samples, 25.0) + np.random.normal(0, 0.05 * self.noise_level, self.num_samples)
        dht_hum = np.full(self.num_samples, 50.0) + np.random.normal(0, 0.2 * self.noise_level, self.num_samples)
        
        # MPU
        mpu_acc_x = np.random.normal(0, 0.01 * self.noise_level, self.num_samples)
        mpu_acc_y = np.random.normal(0, 0.01 * self.noise_level, self.num_samples)
        mpu_acc_z = np.full(self.num_samples, 1.0) + np.random.normal(0, 0.01 * self.noise_level, self.num_samples)
        
        mpu_gyro_x = np.random.normal(0, 0.5 * self.noise_level, self.num_samples)
        mpu_gyro_y = np.random.normal(0, 0.5 * self.noise_level, self.num_samples)
        mpu_gyro_z = np.random.normal(0, 0.5 * self.noise_level, self.num_samples)
        
        # Ultrasonic
        ultra_dist = np.full(self.num_samples, 200.0) + np.random.normal(0, 1.0 * self.noise_level, self.num_samples)
        
        # PIR
        pir_motion = np.zeros(self.num_samples)
        
        df = pd.DataFrame({
            'timestamp': t,
            'dht_temp': dht_temp,
            'dht_hum': dht_hum,
            'mpu_acc_x': mpu_acc_x,
            'mpu_acc_y': mpu_acc_y,
            'mpu_acc_z': mpu_acc_z,
            'mpu_gyro_x': mpu_gyro_x,
            'mpu_gyro_y': mpu_gyro_y,
            'mpu_gyro_z': mpu_gyro_z,
            'ultra_dist': ultra_dist,
            'pir_motion': pir_motion,
            'label': 'NORMAL'
        })
        return df

    def apply_scenario(self, df, scenario_name, fault_start=0.3, fault_end=0.7):
        start_idx = int(self.num_samples * fault_start)
        end_idx = int(self.num_samples * fault_end)
        t_fault = np.linspace(0, 1, end_idx - start_idx) # normalized time for transitions
        
        if scenario_name == 'NORMAL':
            pass
        elif scenario_name == 'OVERHEATING':
            # Temp rises gradually, humidity drops
            df.loc[start_idx:end_idx-1, 'dht_temp'] += t_fault * 20.0 # up to +20C
            df.loc[start_idx:end_idx-1, 'dht_hum'] -= t_fault * 15.0
            df.loc[end_idx:, 'dht_temp'] += 20.0
            df.loc[end_idx:, 'dht_hum'] -= 15.0
            df.loc[start_idx:, 'label'] = 'OVERHEATING'
            
        elif scenario_name == 'SUDDEN_ACCELERATION':
            # Surge in acc_y (forward)
            surge = np.sin(t_fault * np.pi) * 1.5 # up to 1.5g
            df.loc[start_idx:end_idx-1, 'mpu_acc_y'] += surge
            df.loc[start_idx:end_idx-1, 'label'] = 'SUDDEN_ACCELERATION'
            
        elif scenario_name == 'IMPACT_LIKE_EVENT':
            # Very short, high amplitude spike in acc and gyro
            impact_end = min(start_idx + int(self.fps * 0.2), end_idx) # 0.2s duration
            df.loc[start_idx:impact_end, 'mpu_acc_x'] += np.random.normal(0, 5.0, impact_end - start_idx + 1)
            df.loc[start_idx:impact_end, 'mpu_gyro_z'] += np.random.normal(0, 200.0, impact_end - start_idx + 1)
            df.loc[start_idx:impact_end, 'label'] = 'IMPACT_LIKE_EVENT'
            
        elif scenario_name == 'HIGH_VIBRATION':
            df.loc[start_idx:end_idx-1, 'mpu_acc_z'] += np.sin(t_fault * 100 * np.pi) * 0.8
            df.loc[start_idx:end_idx-1, 'mpu_acc_x'] += np.random.normal(0, 0.4, end_idx - start_idx)
            df.loc[start_idx:end_idx-1, 'label'] = 'HIGH_VIBRATION'
            
        elif scenario_name == 'OBSTACLE_APPROACH':
            # Distance decreases linearly
            df.loc[start_idx:end_idx-1, 'ultra_dist'] = np.linspace(200.0, 10.0, end_idx - start_idx) + np.random.normal(0, 0.5, end_idx - start_idx)
            df.loc[end_idx:, 'ultra_dist'] = 10.0 + np.random.normal(0, 0.5, self.num_samples - end_idx)
            df.loc[start_idx:, 'label'] = 'OBSTACLE_APPROACH'
            
        elif scenario_name == 'PIR_ACTIVITY':
            # Trigger PIR in bursts
            df.loc[start_idx:end_idx-1, 'pir_motion'] = np.random.choice([0, 1], size=end_idx - start_idx, p=[0.2, 0.8])
            df.loc[start_idx:end_idx-1, 'label'] = 'PIR_ACTIVITY'
            
        elif scenario_name == 'SENSOR_STUCK':
            # MPU stuck on last value before fault
            prev_idx = max(0, start_idx-1)
            stuck_vals = df.loc[prev_idx, ['mpu_acc_x', 'mpu_acc_y', 'mpu_acc_z', 'mpu_gyro_x', 'mpu_gyro_y', 'mpu_gyro_z']]
            for col in ['mpu_acc_x', 'mpu_acc_y', 'mpu_acc_z', 'mpu_gyro_x', 'mpu_gyro_y', 'mpu_gyro_z']:
                df.loc[start_idx:end_idx-1, col] = stuck_vals[col]
            df.loc[start_idx:end_idx-1, 'label'] = 'SENSOR_STUCK'
            
        elif scenario_name == 'SENSOR_NOISE':
            # Ultrasonic sensor experiences extreme variance
            df.loc[start_idx:end_idx-1, 'ultra_dist'] += np.random.normal(0, 50.0, end_idx - start_idx)
            df.loc[start_idx:end_idx-1, 'label'] = 'SENSOR_NOISE'
            
        elif scenario_name == 'SENSOR_DROPOUT':
            # DHT values drop to NaN
            df.loc[start_idx:end_idx-1, 'dht_temp'] = np.nan
            df.loc[start_idx:end_idx-1, 'label'] = 'SENSOR_DROPOUT'
            
        elif scenario_name == 'MULTI_SENSOR_ANOMALY':
            # High vibration (MPU) + DHT dropout
            df.loc[start_idx:end_idx-1, 'mpu_acc_z'] += np.random.normal(0, 1.0, end_idx - start_idx)
            df.loc[start_idx:end_idx-1, 'dht_temp'] = np.nan
            df.loc[start_idx:end_idx-1, 'label'] = 'MULTI_SENSOR_ANOMALY'
            
        else:
            raise ValueError(f"Unknown scenario: {scenario_name}")
            
        return df

    def generate(self, scenario_name, fault_start=0.3, fault_end=0.7):
        df = self._generate_base()
        return self.apply_scenario(df, scenario_name, fault_start, fault_end)
