import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.paths import SYNTHETIC_DATA_DIR, MODELS_DIR
from ai.features import FeatureExtractor
from ai.models.xgboost_classifier import XGBoostFaultClassifier

def build_dataset(seed: int, target_classes: list, window_size=128, stride=64):
    extractor = FeatureExtractor(fps=50)
    features_list = []
    labels_list = []
    
    for cls in target_classes:
        filename = f"{cls.lower()}_seed{seed}.csv"
        filepath = SYNTHETIC_DATA_DIR / filename
        if not filepath.exists():
            continue
            
        df = pd.read_csv(filepath)
        for start in range(0, len(df) - window_size + 1, stride):
            w = df.iloc[start:start+window_size]
            
            # Check if ANY sample in the window contains the target class
            # Since the file is generated for a specific scenario 'cls', we label it 'cls' if 'cls' appears.
            # Otherwise we fall back to whatever is most common (usually NORMAL)
            unique_labels = w['label'].unique()
            if cls in unique_labels:
                true_label = cls
            else:
                true_label = w['label'].iloc[-1] # fallback
                
            if true_label in target_classes:
                feats = extractor.extract(w)
                features_list.append(feats)
                labels_list.append(true_label)
                
    return pd.DataFrame(features_list), pd.Series(labels_list)

def main():
    model = XGBoostFaultClassifier()
    target_classes = model.classes
    
    print("Building datasets...")
    # Seed 101 for train
    X_train, y_train = build_dataset(101, target_classes, stride=128)
    # Seed 102 for val
    X_val, y_val = build_dataset(102, target_classes, stride=128)
    # Seed 103 for test
    X_test, y_test = build_dataset(103, target_classes, stride=128)
    
    print(f"Train size: {len(X_train)}, Val size: {len(X_val)}, Test size: {len(X_test)}")
    
    print("Training XGBoost...")
    model.fit(X_train, y_train, eval_set=(X_val, y_val))
    model.save(MODELS_DIR)
    print(f"Model saved to {MODELS_DIR}/xgb_model.json")
    
    print("\n--- Evaluation on Test Set ---")
    y_pred = []
    y_true = []
    
    for i in range(len(X_test)):
        row = X_test.iloc[i].to_dict()
        pred = model.predict(row)
        y_pred.append(pred['predicted_class'])
        y_true.append(y_test.iloc[i])
        
    print(classification_report(y_true, y_pred, labels=target_classes, zero_division=0))
    
    # Feature importance
    print("\n--- Feature Importance ---")
    importance = model.model.feature_importances_
    features = model.feature_names
    feat_imp = sorted(zip(features, importance), key=lambda x: x[1], reverse=True)
    
    with open(Path(MODELS_DIR).parent / "docs" / "feature_importance.md", "w") as f:
        f.write("# XGBoost Feature Importance\n\n")
        f.write("| Feature | Importance (Gain) |\n")
        f.write("|---|---|\n")
        for feat, imp in feat_imp:
            line = f"| {feat} | {imp:.4f} |"
            print(line)
            f.write(line + "\n")
            
    print("\nDocumentation saved to docs/feature_importance.md")

if __name__ == "__main__":
    main()
