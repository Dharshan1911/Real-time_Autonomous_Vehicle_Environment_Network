import { useRaven } from '../RavenContext'
import { CheckCircle, AlertTriangle, Shield, Activity, Cpu, Brain, GitMerge, Terminal, RefreshCw, Eye } from 'lucide-react'

const AGENTS = [
  { key: 'isolation_forest', label: 'Isolation Forest', icon: <Brain size={14} />, desc: 'Unsupervised anomaly detection' },
  { key: 'xgboost',          label: 'XGBoost Classifier', icon: <Cpu size={14} />,   desc: 'Supervised fault classification' },
  { key: 'cnn',              label: '1D CNN (Temporal)',  icon: <Activity size={14} />, desc: 'Temporal pattern analysis' },
  { key: 'fusion',           label: 'Fusion Agent',       icon: <GitMerge size={14} />, desc: 'Multi-model consensus' },
  { key: 'decision',         label: 'Decision Agent',     icon: <Terminal size={14} />, desc: 'Action determination' },
  { key: 'recovery',         label: 'Recovery Agent',     icon: <RefreshCw size={14} />, desc: 'Simulated recovery dispatch' },
  { key: 'verification',     label: 'Verification Agent', icon: <Eye size={14} />,    desc: 'Recovery verification' },
]

function agentDot(status: string) {
  return {
    ONLINE:     '#22c55e',
    PROCESSING: '#0ea5e9',
    WARNING:    '#f97316',
    ERROR:      '#ef4444',
  }[status] ?? '#64748b'
}

export function AgentPipelinePanel() {
  const { status, latest } = useRaven()
  const agentStatuses = status?.agents ?? {}

  // Derive "processing" state when sim is running
  const running = status?.running ?? false
  const fusionLevel = latest?.fusion?.level ?? 'NORMAL'
  const isAnomaly = fusionLevel !== 'NORMAL'

  return (
    <div>
      <div className="card-title">Multi-Agent Pipeline</div>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        {/* Pipeline flow visualization */}
        <div className="card" style={{ flex: '0 0 180px' }}>
          <div className="card-title">Data Flow</div>
          {[
            'Sensor Simulation',
            'Feature Engineering',
            'AI Models (×3)',
            'AI Fusion',
            'Decision Agent',
            'Recovery Agent',
            'Verification',
          ].map((step, i, arr) => (
            <div key={step}>
              <div style={{
                padding: '6px 10px',
                borderRadius: 5,
                fontSize: 10,
                background: running ? 'rgba(14,165,233,0.1)' : 'rgba(255,255,255,0.03)',
                border: `1px solid ${running ? 'rgba(14,165,233,0.25)' : 'var(--border)'}`,
                color: running ? 'var(--text-primary)' : 'var(--text-secondary)',
                fontWeight: running ? 600 : 400,
              }}>{step}</div>
              {i < arr.length - 1 && (
                <div className="flow-arrow" style={{ padding: '3px 0', fontSize: 14 }}>↓</div>
              )}
            </div>
          ))}
        </div>

        {/* Agent cards */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {AGENTS.map((agent) => {
            const rawStatus = agentStatuses[agent.key] ?? 'UNKNOWN'
            const effectiveStatus = running && rawStatus === 'ONLINE' ? 'ONLINE' : rawStatus
            const dot = agentDot(effectiveStatus)
            return (
              <div key={agent.key} style={{
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '8px 12px', borderRadius: 6,
                background: 'var(--bg-card-alt)',
                border: `1px solid ${isAnomaly && ['fusion','decision','recovery','verification'].includes(agent.key) ? 'rgba(239,68,68,0.25)' : 'var(--border)'}`,
              }}>
                <div style={{ color: dot }}>{agent.icon}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 11, fontWeight: 700 }}>{agent.label}</div>
                  <div style={{ fontSize: 9, color: 'var(--text-dim)' }}>{agent.desc}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <div className="pulse-dot" style={{ background: dot }} />
                  <span style={{ fontSize: 9, color: dot, fontWeight: 700, letterSpacing: '0.08em' }}>{effectiveStatus}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export function DecisionRecoveryPanel() {
  const { latest } = useRaven()

  const fusion = latest?.fusion
  const decision = latest?.decision
  const recovery = latest?.recovery
  const verification = latest?.verification

  const fusionColor = {
    NORMAL: '#22c55e', SUSPICIOUS: '#eab308', WARNING: '#f97316', CRITICAL: '#ef4444'
  }[fusion?.level ?? 'NORMAL'] ?? '#64748b'

  const verColor = verification?.status === 'RESOLVED' ? '#22c55e' : verification?.status === 'ESCALATED' ? '#ef4444' : '#64748b'

  return (
    <div className="card">
      <div className="card-title">Decision & Recovery Pipeline</div>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {[
          {
            label: 'Fusion State',
            value: fusion?.level ?? '--',
            sub: fusion?.primary_fault ?? '',
            color: fusionColor,
            icon: <GitMerge size={14} />,
          },
          {
            label: 'Decision',
            value: decision?.action_type ?? 'NONE',
            sub: decision?.target ?? '',
            color: '#0ea5e9',
            icon: <Terminal size={14} />,
          },
          {
            label: 'Recovery',
            value: recovery?.action_taken ?? 'NONE',
            sub: recovery?.success === true ? 'Dispatched ✓' : recovery?.success === false ? 'Failed ✗' : 'N/A',
            color: recovery?.success ? '#22c55e' : '#64748b',
            icon: <RefreshCw size={14} />,
          },
          {
            label: 'Verification',
            value: verification?.status ?? 'N/A',
            sub: verification?.message?.slice(0, 40) ?? '',
            color: verColor,
            icon: verification?.status === 'RESOLVED' ? <CheckCircle size={14} /> : <AlertTriangle size={14} />,
          },
        ].map((item) => (
          <div key={item.label} style={{ flex: '1 1 120px', textAlign: 'center', padding: '8px 4px' }}>
            <div style={{ color: item.color, marginBottom: 4 }}>{item.icon}</div>
            <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>{item.label}</div>
            <div style={{ fontSize: 14, fontWeight: 800, color: item.color }}>{item.value}</div>
            <div style={{ fontSize: 9, color: 'var(--text-secondary)', marginTop: 2 }}>{item.sub}</div>
          </div>
        ))}
      </div>

      {recovery?.action_taken && recovery.action_taken !== 'NONE' && (
        <div style={{ marginTop: 12, padding: '8px 10px', background: 'rgba(34,197,94,0.06)', border: '1px solid rgba(34,197,94,0.2)', borderRadius: 6, fontSize: 10, color: 'var(--text-secondary)' }}>
          <Shield size={10} style={{ display: 'inline', marginRight: 5 }} />
          <strong>Software Recovery Note:</strong> Recovery actions are software-level dispatches (simulated). Physical hardware actuation requires QNX target deployment.
        </div>
      )}
    </div>
  )
}
