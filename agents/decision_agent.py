import logging
from agents.contracts import FusionState, DecisionCommand
from agents.message_bus import decision_to_recovery

logger = logging.getLogger(__name__)

class DecisionAgent:
    def process_queue(self, fusion_queue):
        while not fusion_queue.empty():
            state = fusion_queue.get()
            self.process(state)

    def process(self, state: FusionState):
        if state.level == 'NORMAL':
            # No action needed
            return None
            
        command = self._decide_action(state)
        logger.info(f"[DecisionAgent] Decided Action: {command.action_type} on {command.target}")
        decision_to_recovery.put(command)
        return command
        
    def _decide_action(self, state: FusionState) -> DecisionCommand:
        action = 'NONE'
        target = 'NONE'
        
        # Mapping physical and hardware faults to recovery actions
        if state.primary_fault == 'OVERHEATING':
            action = 'THROTTLE_LIMIT'
            target = 'VEHICLE_SYSTEM'
            
        elif state.primary_fault in ['SENSOR_DROPOUT', 'SENSOR_STUCK']:
            action = 'RESET_SENSOR'
            target = 'SENSOR_BUS'
            
        elif state.primary_fault == 'MULTI_SENSOR_ANOMALY':
            action = 'LIMP_MODE'
            target = 'VEHICLE_SYSTEM'
            
        elif state.primary_fault in ['IMPACT_LIKE_EVENT', 'OBSTACLE_APPROACH']:
            action = 'EMERGENCY_STOP'
            target = 'VEHICLE_SYSTEM'
            
        elif state.primary_fault == 'HIGH_VIBRATION':
            action = 'SPEED_REDUCTION'
            target = 'VEHICLE_SYSTEM'
            
        elif state.level == 'SUSPICIOUS':
            action = 'LOG_AND_MONITOR'
            target = 'SYSTEM'
            
        return DecisionCommand(
            action_type=action,
            target=target,
            fusion_state=state
        )
