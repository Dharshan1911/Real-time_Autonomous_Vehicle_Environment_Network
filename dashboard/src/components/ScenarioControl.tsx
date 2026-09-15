import { useRaven } from '../RavenContext'
import { Play, Square, RotateCcw } from 'lucide-react'
import { useState } from 'react'

const SCENARIOS = [
  { id: 'NORMAL',             label: 'Normal',              desc: 'Baseline healthy system operation', color: '#22c55e' },
  { id: 'OVERHEATING',        label: 'Overheating',         desc: 'DHT11 temperature rise (+20°C)', color: '#f97316' },
  { id: 'IMPACT_LIKE_EVENT',  label: 'Impact-Like Event',   desc: 'Short high-amplitude IMU spike', color: '#ef4444' },
  { id: 'HIGH_VIBRATION',     label: 'High Vibration',      desc: 'Sustained oscillation on acc-Z', color: '#f97316' },
  { id: 'OBSTACLE_APPROACH',  label: 'Obstacle Approach',   desc: 'HC-SR04 distance collapses to 10cm', color: '#eab308' },
  { id: 'SENSOR_STUCK',       label: 'Sensor Stuck',        desc: 'MPU6050 all axes frozen', color: '#f97316' },
  { id: 'SENSOR_DROPOUT',     label: 'Sensor Dropout',      desc: 'DHT11 NaN — I2C bus loss', color: '#ef4444' },
  { id: 'MULTI_SENSOR_ANOMALY', label: 'Multi-Sensor Anomaly', desc: 'DHT dropout + MPU vibration', color: '#ef4444' },
]

export function ScenarioControl() {
  const { status, startScenario, stopScenario, resetScenario } = useRaven()
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState('NORMAL')

  const running = status?.running ?? false
  const current = status?.scenario ?? 'NORMAL'

  const handleStart = async (sc: string) => {
    setLoading(true)
    setSelected(sc)
    await startScenario(sc)
    setLoading(false)
  }
  const handleStop = async () => {
    setLoading(true)
    await stopScenario()
    setLoading(false)
  }
  const handleReset = async () => {
    setLoading(true)
    await resetScenario()
    setLoading(false)
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
        <div className="card-title" style={{ margin: 0 }}>Simulation Control</div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-danger" onClick={handleStop} disabled={!running || loading}>
            <Square size={11} /> Stop
          </button>
          <button className="btn btn-ghost" onClick={handleReset} disabled={loading}>
            <RotateCcw size={11} /> Reset
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 8 }}>
        {SCENARIOS.map((sc) => {
          const isActive = current === sc.id && running
          const isSelected = selected === sc.id
          return (
            <div key={sc.id}
              onClick={() => !loading && handleStart(sc.id)}
              style={{
                padding: '10px 12px', borderRadius: 6, cursor: loading ? 'not-allowed' : 'pointer',
                border: `1px solid ${isActive ? sc.color : isSelected ? sc.color + '60' : 'var(--border)'}`,
                background: isActive ? sc.color + '18' : isSelected ? sc.color + '08' : 'var(--bg-card-alt)',
                transition: 'all 0.15s',
                opacity: loading ? 0.6 : 1,
              }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 3 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: isActive ? sc.color : 'var(--text-primary)' }}>
                  {sc.label}
                </div>
                {isActive && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <div className="pulse-dot" style={{ background: sc.color }} />
                    <span style={{ fontSize: 8, color: sc.color, fontWeight: 700 }}>LIVE</span>
                  </div>
                )}
              </div>
              <div style={{ fontSize: 9, color: 'var(--text-dim)' }}>{sc.desc}</div>
              {isActive && (
                <div style={{ marginTop: 6 }}>
                  <button className="btn btn-primary" style={{ fontSize: 9, padding: '2px 8px', pointerEvents: 'none' }}>
                    <Play size={8} /> Running
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
