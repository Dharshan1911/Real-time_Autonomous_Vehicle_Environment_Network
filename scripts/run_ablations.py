import os
import sys
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.train_xgboost import build_dataset
from ai.models.xgboost_classifier import XGBoostFaultClassifier

def run_model_ablation():
    print("\n" + "="*50)
    print("MODEL ABLATION: Decision Tree vs Random Forest vs XGBoost")
    print("="*50)
    model = XGBoostFaultClassifier()
    target_classes = model.classes
    
    print("Building datasets...")
    X_train, y_train = build_dataset(101, target_classes, stride=128)
    X_test, y_test = build_dataset(103, target_classes, stride=128)
    
    results = []

    # 1. Decision Tree
    dt = DecisionTreeClassifier(max_depth=3, random_state=42)
    dt.fit(X_train, y_train)
    dt_preds = dt.predict(X_test)
    dt_acc = accuracy_score(y_test, dt_preds)
    results.append(("Decision Tree (depth=3)", dt_acc))
    
    # 2. Random Forest
    rf = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    results.append(("Random Forest (n=50, depth=4)", rf_acc))
    
    # 3. XGBoost
    xgb = XGBoostFaultClassifier()
    xgb.fit(X_train, y_train, eval_set=(X_test, y_test))
    
    y_pred_xgb = []
    for i in range(len(X_test)):
        row = X_test.iloc[i].to_dict()
        pred = xgb.predict(row)
        y_pred_xgb.append(pred['predicted_class'])
    xgb_acc = accuracy_score(y_test, y_pred_xgb)
    results.append(("XGBoost (n=50, depth=4)", xgb_acc))

    print("\n--- Ablation Results ---")
    print(f"{'Model':<35} | {'Test Accuracy':<15}")
    print("-" * 55)
    for name, acc in results:
        print(f"{name:<35} | {acc:.4f}")

if __name__ == '__main__':
    run_model_ablation()
