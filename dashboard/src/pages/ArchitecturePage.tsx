export function ArchitecturePage() {
  const Box = ({ label, color, sub }: { label: string; color?: string; sub?: string }) => (
    <div style={{
      padding: '10px 16px', borderRadius: 6, textAlign: 'center',
      background: color ? color + '18' : 'var(--bg-card-alt)',
      border: `1px solid ${color ? color + '40' : 'var(--border)'}`,
      minWidth: 160,
    }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: color ?? 'var(--text-primary)' }}>{label}</div>
      {sub && <div style={{ fontSize: 9, color: 'var(--text-dim)', marginTop: 2 }}>{sub}</div>}
    </div>
  )
  const Arrow = () => <div style={{ textAlign: 'center', color: 'var(--accent)', fontSize: 16, lineHeight: 1, padding: '4px 0' }}>↓</div>

  return (
    <div style={{ padding: 16 }}>
      <div className="card-title" style={{ fontSize: 14, marginBottom: 16 }}>System Architecture</div>

      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
        {/* Pipeline column */}
        <div className="card" style={{ flex: '0 1 280px' }}>
          <div className="card-title">Full Pipeline</div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0 }}>
            <Box label="Physical Sensors" color="#64748b" sub="Future: DHT11 · MPU6050 · HC-SR04 · PIR" />
            <Arrow />
            <Box label="Sensor Simulation Layer" color="#0ea5e9" sub="SyntheticTelemetryEngine @ 50Hz" />
            <Arrow />
            <Box label="Sensor Abstraction (ABC)" color="#0ea5e9" sub="SensorInterface — hardware-agnostic" />
            <Arrow />
            <Box label="Window Buffer (128 samples)" color="#0ea5e9" sub="2.56s windows @ 50Hz" />
            <Arrow />
            <Box label="Feature Engineering (13 features)" color="#a855f7" sub="Magnitudes · ZCR · ROC · Validity" />
            <Arrow />
            <div style={{ display: 'flex', gap: 8, width: '100%', justifyContent: 'center' }}>
              <div style={{ flex: 1, textAlign: 'center' }}>
                <Box label="Isolation Forest" color="#f97316" sub="Unsupervised" />
              </div>
              <div style={{ flex: 1, textAlign: 'center' }}>
                <Box label="XGBoost" color="#f97316" sub="Tabular" />
              </div>
              <div style={{ flex: 1, textAlign: 'center' }}>
                <Box label="1D CNN" color="#a855f7" sub="Temporal" />
              </div>
            </div>
            <Arrow />
            <Box label="AI Fusion Agent" color="#eab308" sub="Rule-based — NORMAL/SUSPICIOUS/WARNING/CRITICAL" />
            <Arrow />
            <Box label="Decision Agent" color="#0ea5e9" sub="Action mapping" />
            <Arrow />
            <Box label="Recovery Agent" color="#22c55e" sub="Software recovery dispatch (stubbed)" />
            <Arrow />
            <Box label="Verification Agent" color="#22c55e" sub="Dispatch confirmation" />
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Current environment */}
          <div className="card" style={{ borderColor: 'rgba(14,165,233,0.3)' }}>
            <div className="card-title">Current Environment</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {[
                ['OS', 'Windows 10/11 (x86_64)'],
                ['Runtime', 'Python 3.10 venv'],
                ['ML Framework', 'scikit-learn + XGBoost + ONNX'],
                ['API Server', 'FastAPI + uvicorn (port 8000)'],
                ['Frontend', 'React 19 + Vite + Tailwind CSS'],
                ['QNX', 'QCC cross-compiles AArch64 ELF stubs'],
              ].map(([l, v]) => (
                <div key={l} style={{ padding: '8px 10px', background: 'var(--bg-card-alt)', borderRadius: 5 }}>
                  <div style={{ fontSize: 9, color: 'var(--text-dim)' }}>{l}</div>
                  <div style={{ fontSize: 11, fontWeight: 600 }}>{v}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Future deployment */}
          <div className="card" style={{ borderColor: 'rgba(34,197,94,0.25)' }}>
            <div className="card-title">Future Deployment Target</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {[
                ['Hardware', 'Raspberry Pi 4 (4GB RAM)'],
                ['OS', 'QNX Neutrino RTOS 8.0'],
                ['Sensor Bus', 'I2C (MPU6050) + GPIO (DHT11, PIR)'],
                ['C Driver', 'qnx/src/sensor_bridge.c'],
                ['IPC', 'QNX Message Passing / Unix sockets'],
                ['Status', 'NOT YET CONNECTED'],
              ].map(([l, v]) => (
                <div key={l} style={{ padding: '8px 10px', background: 'var(--bg-card-alt)', borderRadius: 5 }}>
                  <div style={{ fontSize: 9, color: 'var(--text-dim)' }}>{l}</div>
                  <div style={{ fontSize: 11, fontWeight: 600, color: l === 'Status' ? '#ef4444' : 'var(--text-primary)' }}>{v}</div>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 12, padding: '8px 10px', background: 'rgba(34,197,94,0.06)', border: '1px solid rgba(34,197,94,0.2)', borderRadius: 6, fontSize: 9, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              The SensorInterface ABC ensures that replacing the SyntheticTelemetryEngine with real QNX sensor drivers requires zero rewrites of the AI pipeline or agent layer.
            </div>
          </div>

          {/* Hardware readiness */}
          <div className="card" style={{ borderColor: 'rgba(71,85,105,0.3)' }}>
            <div className="card-title">Hardware Readiness</div>
            {[
              { label: 'Raspberry Pi 4 (4GB)', status: 'NOT CONNECTED' },
              { label: 'DHT11 (Thermal)', status: 'NOT CONNECTED' },
              { label: 'MPU6050 (IMU 6-DoF)', status: 'NOT CONNECTED' },
              { label: 'HC-SR04 (Ultrasonic)', status: 'NOT CONNECTED' },
              { label: 'PIR (Motion)', status: 'NOT CONNECTED' },
              { label: 'QNX sensor_bridge.c', status: 'COMPILED (STUB)' },
            ].map(({ label, status }) => (
              <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ fontSize: 10, color: 'var(--text-secondary)' }}>{label}</span>
                <span style={{ fontSize: 9, fontWeight: 700, color: status.startsWith('NOT') ? '#ef4444' : '#eab308' }}>{status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
