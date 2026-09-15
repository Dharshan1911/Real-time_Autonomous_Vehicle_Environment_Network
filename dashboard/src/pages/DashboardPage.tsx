import { SystemHeader } from '../components/SystemHeader'
import { SensorOverview } from '../components/SensorOverview'
import { LiveTelemetryChart } from '../components/LiveTelemetryChart'
import { AIAnalysisPanel } from '../components/AIAnalysisPanel'
import { AgentPipelinePanel, DecisionRecoveryPanel } from '../components/AgentPipelinePanel'
import { ScenarioControl } from '../components/ScenarioControl'
import { EventTimeline } from '../components/EventTimeline'
import { useRaven } from '../RavenContext'

export function DashboardPage() {
  const { status } = useRaven()
  const tick = status?.tick ?? 0

  return (
    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <SystemHeader />

      {/* System health bar */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        {[
          { label: 'Scenarios Processed', value: tick },
          { label: 'Active Agents', value: 7 },
          { label: 'Mode', value: 'SIMULATION' },
          { label: 'Hardware', value: 'NOT CONNECTED' },
          { label: 'Models', value: status?.models_loaded ? 'LOADED' : 'ERROR' },
          { label: 'Running', value: status?.running ? 'YES' : 'NO' },
        ].map(({ label, value }) => (
          <div key={label} className="card" style={{ flex: '1 1 110px', textAlign: 'center', padding: '10px 8px' }}>
            <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>{value}</div>
          </div>
        ))}
      </div>

      <SensorOverview />
      <LiveTelemetryChart />
      <AIAnalysisPanel />

      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <div style={{ flex: '1 1 400px' }}>
          <AgentPipelinePanel />
        </div>
        <div style={{ flex: '1 1 300px' }}>
          <EventTimeline />
        </div>
      </div>

      <DecisionRecoveryPanel />
      <ScenarioControl />
    </div>
  )
}
