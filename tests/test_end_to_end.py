import os
import sys
import logging
import pytest
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.contracts import ModelOutputs, TelemetryMetadata
from agents.fusion_agent import FusionAgent
from agents.decision_agent import DecisionAgent
from agents.recovery_agent import RecoveryAgent
from agents.verification_agent import VerificationAgent
from agents.message_bus import fusion_to_decision, decision_to_recovery, recovery_to_verification

def test_end_to_end_critical_fault():
    # 1. Simulate AI Outputs (e.g., A Sensor Dropout)
    # Both IF and XGB flag it, CNN misses it or flags something else
    outputs = ModelOutputs(
        iso_is_anomaly=True,
        iso_score=-0.8,
        xgb_class='SENSOR_DROPOUT',
        xgb_confidence=0.99,
        xgb_probs={'SENSOR_DROPOUT': 0.99, 'NORMAL': 0.01},
        cnn_class='NORMAL', # CNN might miss a static dropout if not trained perfectly on it
        cnn_confidence=0.6,
        cnn_probs={'NORMAL': 0.6, 'SENSOR_DROPOUT': 0.1}
    )
    
    metadata = TelemetryMetadata(
        timestamp_start=0.0,
        timestamp_end=2.56,
        window_size=128
    )
    
    # 2. Instantiate Agents
    fusion_agent = FusionAgent()
    decision_agent = DecisionAgent()
    recovery_agent = RecoveryAgent()
    verification_agent = VerificationAgent()
    
    # 3. Pipeline Execution
    # Fusion
    state = fusion_agent.process(outputs, metadata)
    assert state.level == 'CRITICAL'
    assert state.primary_fault == 'SENSOR_DROPOUT'
    
    # Decision
    decision_agent.process_queue(fusion_to_decision)
    assert not decision_to_recovery.empty()
    
    # Recovery
    recovery_agent.process_queue(decision_to_recovery)
    assert not recovery_to_verification.empty()
    
    # Verification
    # Instead of queue processing, we can manually pull to check the result
    action = recovery_to_verification.get()
    result = verification_agent.process(action)
    
    assert action.action_taken == 'RESET_SENSOR'
    assert result.status == 'RESOLVED'

def test_end_to_end_unsupervised_outlier():
    # Models predict NORMAL, but IF strongly flags
    outputs = ModelOutputs(
        iso_is_anomaly=True,
        iso_score=-0.7,
        xgb_class='NORMAL',
        xgb_confidence=0.90,
        xgb_probs={'NORMAL': 0.90},
        cnn_class='NORMAL',
        cnn_confidence=0.85,
        cnn_probs={'NORMAL': 0.85}
    )
    
    metadata = TelemetryMetadata(0.0, 2.56, 128)
    fusion_agent = FusionAgent()
    state = fusion_agent.process(outputs, metadata)
    
    assert state.level == 'SUSPICIOUS'
    assert state.primary_fault == 'UNKNOWN_ANOMALY'
    
    # Decision
    decision_agent = DecisionAgent()
    cmd = decision_agent.process(state)
    assert cmd.action_type == 'LOG_AND_MONITOR'

def test_end_to_end_normal():
    outputs = ModelOutputs(
        iso_is_anomaly=False,
        iso_score=0.5,
        xgb_class='NORMAL',
        xgb_confidence=0.99,
        xgb_probs={'NORMAL': 0.99},
        cnn_class='NORMAL',
        cnn_confidence=0.95,
        cnn_probs={'NORMAL': 0.95}
    )
    metadata = TelemetryMetadata(0.0, 2.56, 128)
    fusion_agent = FusionAgent()
    state = fusion_agent.process(outputs, metadata)
    
    assert state.level == 'NORMAL'
    
    decision_agent = DecisionAgent()
    cmd = decision_agent.process(state)
    assert cmd is None # No action required
