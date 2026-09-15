import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.paths import SYNTHETIC_DATA_DIR, MODELS_DIR
from config.model_config import ISO_FOREST_CONTAMINATION
from ai.features import FeatureExtractor
from ai.models.isolation_forest import IsolationForestModel

def window_dataframe(df, window_size=128, stride=64):
    windows = []
    for start in range(0, len(df) - window_size + 1, stride):
        windows.append(df.iloc[start:start+window_size])
    return windows

def main():
    print("Loading NORMAL synthetic telemetry for training...")
    # Use the 300s long seed=1 generation for training baseline
    normal_file = SYNTHETIC_DATA_DIR / "normal_seed1.csv"
    if not normal_file.exists():
        print(f"Error: Could not find {normal_file}. Run simulation generation first.")
        return
        
    df = pd.read_csv(normal_file)
    print(f"Loaded {len(df)} normal samples.")
    
    print("Extracting features from sliding windows...")
    extractor = FeatureExtractor(fps=50)
    windows = window_dataframe(df, window_size=128, stride=128)
    
    if not windows:
        windows = [df]

    features_list = []
    for w in windows:
        features_list.append(extractor.extract(w))
        
    features_df = pd.DataFrame(features_list)
    
    print(f"Extracted {len(features_df)} feature vectors.")
    print(f"Training Isolation Forest with contamination={ISO_FOREST_CONTAMINATION}...")
    
    model = IsolationForestModel(contamination=ISO_FOREST_CONTAMINATION)
    model.fit(features_df)
    
    # CRIT-2: Empirical Threshold
    # Predict on the training (or validation) set to get unconstrained scores
    print("Calculating empirical threshold from 1st percentile of normal scores...")
    X_scaled = model.scaler.transform(np.nan_to_num(features_df[model.feature_names].values))
    scores = model.model.score_samples(X_scaled)
    # The 1st percentile (0.01) of normal scores becomes our threshold
    empirical_threshold = np.percentile(scores, 1.0)
    print(f"Empirical Threshold (1st percentile): {empirical_threshold:.4f}")
    
    # Save this threshold into the model
    model.empirical_threshold = empirical_threshold
    
    model.save(MODELS_DIR)
    print(f"Model saved to {MODELS_DIR}")

if __name__ == "__main__":
    main()
