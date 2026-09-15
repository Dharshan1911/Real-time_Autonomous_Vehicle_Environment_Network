from agents.message_bus import decision_to_recovery, AlertEvent, recovery_to_verification
from agents.recovery_agent import RecoveryAgent

def test_agents_communication():
    # Simulate decision agent pushing an alert
    decision_to_recovery.put(AlertEvent("HIGH", "Test Alert"))
    
    # Recovery agent processes
    agent = RecoveryAgent()
    agent.process_queue()
    
    # Should result in a message to verification
    assert not recovery_to_verification.empty()
    action = recovery_to_verification.get()
    assert action.action_taken == "Log and Notify"
