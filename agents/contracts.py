from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class TelemetryMetadata:
    timestamp_start: float
    timestamp_end: float
    window_size: int

@dataclass
class ModelOutputs:
    # Isolation Forest
    iso_is_anomaly: bool
    iso_score: float 
    
    # XGBoost
    xgb_class: str
    xgb_confidence: float
    xgb_probs: Dict[str, float]
    
    # CNN 1D
    cnn_class: str
    cnn_confidence: float
    cnn_probs: Dict[str, float]

@dataclass
class FusionState:
    level: str # 'NORMAL', 'SUSPICIOUS', 'WARNING', 'CRITICAL'
    primary_fault: str
    confidence: float
    reasoning: str
    metadata: TelemetryMetadata

@dataclass
class DecisionCommand:
    action_type: str # e.g., 'NONE', 'RESET_SENSOR', 'LIMP_MODE', 'THROTTLE_LIMIT'
    target: str 
    fusion_state: FusionState

@dataclass
class RecoveryAction:
    action_taken: str
    target: str
    success: bool
    timestamp: float
    fusion_state: FusionState

@dataclass
class VerificationResult:
    original_fault: str
    status: str # 'RESOLVED', 'PERSISTENT', 'ESCALATED'
    message: str
