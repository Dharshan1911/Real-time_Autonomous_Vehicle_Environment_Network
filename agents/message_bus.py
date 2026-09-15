import queue

# Centralized message queues for inter-agent communication
# This decouples the agents, allowing them to run independently 
# in the eventual QNX threaded environment.

# Fusion -> Decision
fusion_to_decision = queue.Queue()

# Decision -> Recovery
decision_to_recovery = queue.Queue()

# Recovery -> Verification
recovery_to_verification = queue.Queue()

# Telemetry/Simulation -> Fusion (optional input queue for end-to-end)
telemetry_to_fusion = queue.Queue()
