import os
import sys
import logging
import time
import argparse
from pathlib import Path
import numpy as np

# Setup logging
os.makedirs("logs", exist_ok=True)
# Configure file logger with details, but keep stdout clean for the dashboard
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    filename="logs/demo_run.log",
    filemode='w'
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.engine import SyntheticTelemetryEngine
from ai.features import FeatureExtractor
from ai.models.isolation_forest import IsolationForestModel
from ai.models.xgboost_classifier import XGBoostFaultClassifier
from ai.models.cnn_1d import TemporalCNNModel

from agents.contracts import ModelOutputs, TelemetryMetadata
from agents.fusion_agent import FusionAgent
from agents.decision_agent import DecisionAgent
from agents.recovery_agent import RecoveryAgent
from agents.verification_agent import VerificationAgent
from agents.message_bus import (
    fusion_to_decision, 
    decision_to_recovery, 
    recovery_to_verification
)

from config.paths import MODELS_DIR

def run_scenario(scenario_name, engine, feature_extractor, iso_model, xgb_model, cnn_model, 
                 fusion_agent, decision_agent, recovery_agent, verification_agent):
    print(f"\n{'='*80}")
    print(f" SCENARIO: {scenario_name}")
    print(f"{'='*80}")
    
    # Generate 128 samples (2.56 seconds at 50fps)
    # The scenario will start fault at 0.0 (whole window) to guarantee detection for demo
    df = engine.generate(scenario_name, fault_start=0.0, fault_end=1.0)
    df_window = df.iloc[:128]
    
    true_label = df_window['label'].iloc[-1]
    
    print(f"\n[1/5] SENSOR TELEMETRY (128 samples / 2.56s window)")
    print(f"      Label Ground Truth: {df_window['label'].unique()}")
    print(f"      DHT Temp Range: {df_window['dht_temp'].min():.1f} - {df_window['dht_temp'].max():.1f} C")
    print(f"      MPU Z Range: {df_window['mpu_acc_z'].min():.2f} - {df_window['mpu_acc_z'].max():.2f} g")
    
    # Feature Extraction
    features = feature_extractor.extract(df_window)
    print(f"\n[2/5] FEATURE ENGINEERING")
    print(f"      Extracted 13 scalar features.")
    print(f"      Temp ROC: {features['temp_roc']:.2f}, Z-Vibration ZCR: {features['vibration_zcr']:.2f}, DHT Valid: {features['dht_valid']}")
    
    # Model Inference
    print(f"\n[3/5] AI MODEL INFERENCE")
    
    # Isolation Forest
    iso_res = iso_model.predict(features)
    print(f"      -> Isolation Forest: Anomaly={iso_res['is_anomaly']} (Score: {iso_res['anomaly_score']:.2f})")
    
    # XGBoost
    xgb_res = xgb_model.predict(features)
    print(f"      -> XGBoost (Tabular): Class={xgb_res['predicted_class']} (Conf: {xgb_res['confidence']:.2f})")
    
    # CNN
    cnn_res = cnn_model.predict(df_window)
    print(f"      -> CNN 1D (Temporal): Class={cnn_res['predicted_class']} (Conf: {cnn_res['confidence']:.2f}, Latency: {cnn_res['latency_ms']:.2f}ms)")
    
    outputs = ModelOutputs(
        iso_is_anomaly=iso_res['is_anomaly'],
        iso_score=iso_res['anomaly_score'],
        xgb_class=xgb_res['predicted_class'],
        xgb_confidence=xgb_res['confidence'],
        xgb_probs=xgb_res['class_probabilities'],
        cnn_class=cnn_res['predicted_class'],
        cnn_confidence=cnn_res['confidence'],
        cnn_probs=cnn_res['class_probabilities']
    )
    
    metadata = TelemetryMetadata(
        timestamp_start=df_window['timestamp'].iloc[0],
        timestamp_end=df_window['timestamp'].iloc[-1],
        window_size=128
    )
    
    # Multi-Agent Pipeline
    print(f"\n[4/5] MULTI-AGENT FUSION & DECISION")
    fusion_state = fusion_agent.process(outputs, metadata)
    print(f"      -> Fusion State: {fusion_state.level}")
    print(f"      -> Primary Fault: {fusion_state.primary_fault} (Conf: {fusion_state.confidence:.2f})")
    print(f"      -> Reasoning: {fusion_state.reasoning}")
    
    decision_agent.process_queue(fusion_to_decision)
    
    print(f"\n[5/5] RECOVERY & VERIFICATION")
    # Small sleep to represent message bus propagation
    time.sleep(0.1)
    
    if decision_to_recovery.empty():
        print(f"      -> Action: NONE")
    else:
        while not decision_to_recovery.empty():
            cmd = decision_to_recovery.queue[0]
            print(f"      -> Decision: {cmd.action_type} targeting {cmd.target}")
            recovery_agent.process_queue(decision_to_recovery)
            
    if recovery_to_verification.empty():
        print(f"      -> Verification: No recovery action to verify.")
    else:
        while not recovery_to_verification.empty():
            action = recovery_to_verification.queue[0]
            print(f"      -> Recovery Executed: {action.action_taken} (Success: {action.success})")
            results = verification_agent.process_queue(recovery_to_verification)
            for res in results:
                print(f"      -> Verification Status: {res.status} - {res.message}")
                
    return {
        'true': true_label,
        'xgb': xgb_res['predicted_class'],
        'cnn': cnn_res['predicted_class'],
        'fusion': fusion_state.primary_fault
    }

def print_confusion_matrix(results):
    from sklearn.metrics import confusion_matrix
    y_true = [r['true'] for r in results]
    y_fusion = [r['fusion'] for r in results]
    
    classes = sorted(list(set(y_true + y_fusion)))
    cm = confusion_matrix(y_true, y_fusion, labels=classes)
    
    print(f"\n{'='*80}")
    print(" DEMO CONFUSION MATRIX (Fusion Agent Results)")
    print(f"{'='*80}")
    print(f"{'True / Pred':<22}", end="")
    for c in classes:
        # short name for columns
        print(f"{c[:8]:>9}", end="")
    print("\n" + "-"*80)
    for i, c1 in enumerate(classes):
        print(f"{c1:<22}", end="")
        for j, c2 in enumerate(classes):
            print(f"{cm[i, j]:>9}", end="")
        print()

def main():
    parser = argparse.ArgumentParser(description="RAVEN Demo Runner")
    parser.add_argument('--noise_level', type=float, default=1.0, help="Noise level for the synthetic telemetry engine (default: 1.0)")
    args = parser.parse_args()

    print(f"\nInitializing RAVEN Demonstration Engine (Noise Level: {args.noise_level})...")
    
    # Load Models
    iso_model = IsolationForestModel(model_path=MODELS_DIR)
    xgb_model = XGBoostFaultClassifier(model_path=MODELS_DIR)
    cnn_model = TemporalCNNModel(model_path=MODELS_DIR)
    
    if not (iso_model.is_trained and xgb_model.is_trained and cnn_model.is_trained):
        print("Error: Models must be trained before running the demo.")
        return
        
    # Initialize Core
    engine = SyntheticTelemetryEngine(fps=50, duration=2.56, seed=42, noise_level=args.noise_level) # Exactly 1 window
    feature_extractor = FeatureExtractor(fps=50)
    
    # Initialize Agents
    fusion_agent = FusionAgent()
    decision_agent = DecisionAgent()
    recovery_agent = RecoveryAgent()
    verification_agent = VerificationAgent()
    
    scenarios = [
        'NORMAL',
        'OVERHEATING',
        'IMPACT_LIKE_EVENT',
        'HIGH_VIBRATION',
        'OBSTACLE_APPROACH',
        'SENSOR_STUCK',
        'SENSOR_DROPOUT',
        'MULTI_SENSOR_ANOMALY'
    ]
    
    all_results = []
    
    for sc in scenarios:
        engine.seed += 1
        np.random.seed(engine.seed)
        res = run_scenario(sc, engine, feature_extractor, iso_model, xgb_model, cnn_model, 
                     fusion_agent, decision_agent, recovery_agent, verification_agent)
        all_results.append(res)
        time.sleep(0.1)
        
    print_confusion_matrix(all_results)
        
    print(f"\n{'='*80}")
    print("Demonstration complete. Detailed logs saved to logs/demo_run.log")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
