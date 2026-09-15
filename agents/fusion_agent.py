import logging
from agents.contracts import ModelOutputs, FusionState, TelemetryMetadata
from agents.message_bus import fusion_to_decision

logger = logging.getLogger(__name__)

class FusionAgent:
    def process(self, models: ModelOutputs, metadata: TelemetryMetadata):
        state = self._fuse(models, metadata)
        logger.info(f"[FusionAgent] Generated State: {state.level} | Fault: {state.primary_fault} | Reason: {state.reasoning}")
        fusion_to_decision.put(state)
        return state

    def _fuse(self, models: ModelOutputs, metadata: TelemetryMetadata) -> FusionState:
        # Hardware specific classes that XGBoost handles best
        hardware_faults = ['SENSOR_DROPOUT', 'MULTI_SENSOR_ANOMALY', 'SENSOR_STUCK']
        
        # 1. Unanimous Normal
        if models.xgb_class == 'NORMAL' and models.cnn_class == 'NORMAL' and not models.iso_is_anomaly:
            return FusionState(
                level='NORMAL',
                primary_fault='NORMAL',
                confidence=max(models.xgb_confidence, models.cnn_confidence),
                reasoning="All models agree on NORMAL.",
                metadata=metadata
            )
            
        # 2. Explicit Hardware Failure via XGBoost
        if models.xgb_class in hardware_faults and models.xgb_confidence > 0.75:
            return FusionState(
                level='CRITICAL',
                primary_fault=models.xgb_class,
                confidence=models.xgb_confidence,
                reasoning=f"XGBoost detected critical hardware fault {models.xgb_class} with high confidence.",
                metadata=metadata
            )
            
        # 3. Supervised Agreement
        if models.xgb_class == models.cnn_class and models.xgb_class != 'NORMAL':
            avg_conf = (models.xgb_confidence + models.cnn_confidence) / 2.0
            return FusionState(
                level='CRITICAL',
                primary_fault=models.xgb_class,
                confidence=avg_conf,
                reasoning=f"XGBoost and CNN agree on physical fault {models.xgb_class}.",
                metadata=metadata
            )
            
        # 4. Supervised Disagreement
        if models.xgb_class != models.cnn_class:
            # Tie breaker
            highest_conf_class = models.xgb_class if models.xgb_confidence > models.cnn_confidence else models.cnn_class
            highest_conf_val = max(models.xgb_confidence, models.cnn_confidence)
            
            if models.iso_is_anomaly:
                return FusionState(
                    level='WARNING',
                    primary_fault=highest_conf_class,
                    confidence=highest_conf_val,
                    reasoning=f"Models disagree, but IsolationForest confirms anomaly. Falling back to highest conf class: {highest_conf_class}.",
                    metadata=metadata
                )
            else:
                return FusionState(
                    level='SUSPICIOUS',
                    primary_fault=highest_conf_class,
                    confidence=highest_conf_val * 0.5, # Penalize confidence
                    reasoning=f"Models disagree and IF shows normal. Unsure. Highest conf was {highest_conf_class}.",
                    metadata=metadata
                )
                    
        # 5. Unsupervised Outlier
        if models.xgb_class == 'NORMAL' and models.cnn_class == 'NORMAL' and models.iso_is_anomaly:
            return FusionState(
                level='SUSPICIOUS',
                primary_fault='UNKNOWN_ANOMALY',
                confidence=0.5,
                reasoning=f"Supervised models indicate NORMAL, but Isolation Forest detected a structural outlier (score: {models.iso_score:.2f}).",
                metadata=metadata
            )
            
        # Fallback
        return FusionState(
            level='WARNING',
            primary_fault='UNHANDLED_STATE',
            confidence=0.0,
            reasoning="State fell through fusion logic.",
            metadata=metadata
        )
