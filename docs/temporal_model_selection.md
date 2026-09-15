# Temporal Model Selection

## Candidates
1. **LSTM (Long Short-Term Memory):** Traditional RNN. Great for sequence modeling but suffers from sequential bottlenecks (cannot compute timestep *T* before *T-1*). This results in slow inference on CPUs (like the RPi4) due to poor parallelization.
2. **GRU (Gated Recurrent Unit):** Simpler than LSTM, slightly faster, but shares the same sequential CPU bottleneck.
3. **TCN (Temporal Convolutional Network):** Uses dilated causal convolutions. Highly parallelizable and captures long-range dependencies efficiently. Excellent performance, but can be overkill in architecture for very short 128-sample windows.
4. **Lightweight 1D CNN:** Standard 1D convolutions (non-causal is fine if processing full buffered windows). Extremely fast, highly parallelizable on generic ARMs, and features a tiny memory footprint. Perfect for RAVEN's short 2.56s (128-sample) windows.

## Selection: Lightweight 1D CNN
Given the system constraints (Raspberry Pi 4 target, QNX embedded environment, strict latency limitations, and short 128-sample multi-channel windows), a **Lightweight 1D CNN** is the optimal choice. 

It guarantees ultra-low inference latency on standard ARM CPUs without an accelerator, trivially exports to ONNX (ensuring the inference agent remains framework-independent and doesn't need heavy PyTorch bindings on the RPi), and satisfies the "simplest model that provides meaningful temporal information" directive.

## Role of Datasets
- **RAVEN Synthetic Telemetry:** Used as the *primary and exclusive dataset* to classify specific vehicle fault states based on temporal features.
- **UCI HAR:** Plays an *auxiliary role*. It is strictly used to explore the 1D CNN structural capacity on real-world 6-axis IMU data to ensure the network can extract physical kinetic patterns. **It is NOT used to detect vehicle faults.**
