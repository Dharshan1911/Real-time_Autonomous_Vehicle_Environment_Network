import { useState } from 'react'
import { useRaven } from '../RavenContext'
import { SensorOverview } from '../components/SensorOverview'
import { AIAnalysisPanel } from '../components/AIAnalysisPanel'
import { AgentPipelinePanel, DecisionRecoveryPanel } from '../components/AgentPipelinePanel'
import { Square } from 'lucide-react'

const DEMO_SCENARIOS = [
  { id: 'NORMAL', label: '1. Normal Operation', color: '#22c55e', desc: 'All sensors healthy. All models output NORMAL.' },
  { id: 'IMPACT_LIKE_EVENT', label: '2. Impact-Like Event', color: '#ef4444', desc: 'Short high-amplitude IMU spike → CNN detects temporal shape → Fusion: CRITICAL → Emergency Stop.' },
  { id: 'SENSOR_STUCK', label: '3. Sensor Stuck', color: '#f97316', desc: 'MPU6050 all axes frozen → XGBoost detects zero-variance → Fusion: CRITICAL → Reset Sensor.' },
  { id: 'OVERHEATING', label: '4. Overheating', color: '#f97316', desc: 'DHT11 rises +20°C → XGBoost + CNN detect → Fusion: CRITICAL → Throttle Limit.' },
  { id: 'SENSOR_DROPOUT', label: '5. Sensor Dropout', color: '#ef4444', desc: 'DHT11 NaN → validity flag fires → Fusion: CRITICAL → Reset Sensor Bus.' },
]

export function PresentationMode() {
  const { startScenario, stopScenario, latest } = useRaven()
  const [active, setActive] = useState<string | null>(null)

  const handleSelect = async (sc: string) => {
    setActive(sc)
    await startScenario(sc)
  }
  const handleStop = async () => {
    await stopScenario()
    setActive(null)
  }

  const fusionLevel = latest?.fusion?.level ?? 'NORMAL'
  const fusionColor = { NORMAL: '#22c55e', SUSPICIOUS: '#eab308', WARNING: '#f97316', CRITICAL: '#ef4444' }[fusionLevel] ?? '#64748b'

  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '100vh', padding: 0 }}>
      {/* Presentation header */}
      <div style={{
        background: 'linear-gradient(90deg, #0a0e1a, #0f172a)',
        borderBottom: '1px solid var(--border)',
        padding: '12px 24px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div>
          <div style={{ fontSize: 22, fontWeight: 900, letterSpacing: '0.2em', color: 'var(--text-primary)' }}>RAVEN</div>
          <div style={{ fontSize: 9, color: 'var(--accent)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
            Presentation Mode — Simulation
          </div>
        </div>
        <div style={{
          padding: '8px 20px', borderRadius: 6,
          background: fusionColor + '20', border: `2px solid ${fusionColor}`,
          fontSize: 18, fontWeight: 900, color: fusionColor, letterSpacing: '0.1em',
        }}>
          {fusionLevel}
        </div>
      </div>

      <div style={{ display: 'flex', height: 'calc(100vh - 60px)' }}>
        {/* Scenario selector sidebar */}
        <div style={{
          width: 240, background: '#0a0e1a', borderRight: '1px solid var(--border)',
          padding: 16, display: 'flex', flexDirection: 'column', gap: 8, overflowY: 'auto',
        }}>
          <div className="card-title">Demo Scenarios</div>
          {DEMO_SCENARIOS.map(sc => (
            <div key={sc.id}
              onClick={() => handleSelect(sc.id)}
              style={{
                padding: '10px 12px', borderRadius: 6, cursor: 'pointer',
                border: `1px solid ${active === sc.id ? sc.color : 'var(--border)'}`,
                background: active === sc.id ? sc.color + '18' : 'var(--bg-card)',
                transition: 'all 0.15s',
              }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: active === sc.id ? sc.color : 'var(--text-primary)', marginBottom: 3 }}>
                {sc.label}
              </div>
              <div style={{ fontSize: 9, color: 'var(--text-dim)', lineHeight: 1.5 }}>{sc.desc}</div>
              {active === sc.id && (
                <div style={{ marginTop: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
                  <div className="pulse-dot" style={{ background: sc.color }} />
                  <span style={{ fontSize: 8, color: sc.color, fontWeight: 700 }}>RUNNING</span>
                </div>
              )}
            </div>
          ))}
          {active && (
            <button className="btn btn-danger" onClick={handleStop} style={{ marginTop: 8 }}>
              <Square size={11} /> Stop
            </button>
          )}
        </div>

        {/* Main panel */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <SensorOverview />
          <AIAnalysisPanel />
          <DecisionRecoveryPanel />
          <AgentPipelinePanel />
        </div>
      </div>
    </div>
  )
}
