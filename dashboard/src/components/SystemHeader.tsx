import { useRaven } from '../RavenContext'
import { Activity, Cpu, AlertTriangle, CheckCircle, WifiOff } from 'lucide-react'

function levelBadge(level: string) {
  const map: Record<string, string> = {
    NORMAL: 'badge badge-normal',
    SUSPICIOUS: 'badge badge-suspicious',
    WARNING: 'badge badge-warning',
    CRITICAL: 'badge badge-critical',
    ONLINE: 'badge badge-normal',
    ERROR: 'badge badge-critical',
    INFO: 'badge badge-info',
    OFFLINE: 'badge badge-offline',
  }
  return map[level?.toUpperCase()] ?? 'badge badge-info'
}

export function SystemHeader() {
  const { status, connected, error, latest } = useRaven()

  const fusionLevel = latest?.fusion?.level ?? 'NORMAL'
  const uptime = status ? formatUptime(status.uptime_seconds) : '--'

  return (
    <div className="card" style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 32, height: 32, background: 'var(--accent)', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Activity size={18} color="#fff" />
            </div>
            <div>
              <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: '0.15em', color: 'var(--text-primary)' }}>RAVEN</div>
              <div style={{ fontSize: 9, color: 'var(--text-secondary)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Multi-Agent Vehicle Analysis Platform</div>
            </div>
          </div>

          <div className="sim-banner">
            <Cpu size={12} />
            SIMULATION MODE — Raspberry Pi Not Connected
          </div>
        </div>

        {/* Status row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Scenario</div>
            <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent)' }}>{status?.scenario ?? '--'}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Uptime</div>
            <div style={{ fontSize: 12, fontWeight: 700 }}>{uptime}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Fusion</div>
            <span className={levelBadge(fusionLevel)}>{fusionLevel}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {connected
              ? <><div className="pulse-dot" style={{ background: '#22c55e' }} /><CheckCircle size={14} color="#22c55e" /></>
              : <><WifiOff size={14} color="#ef4444" /><span style={{ color: '#ef4444', fontSize: 10 }}>OFFLINE</span></>
            }
          </div>
        </div>
      </div>

      {error && (
        <div style={{ marginTop: 10, padding: '8px 12px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 6, color: '#ef4444', fontSize: 11, display: 'flex', gap: 6, alignItems: 'center' }}>
          <AlertTriangle size={12} /> {error}
        </div>
      )}
    </div>
  )
}

function formatUptime(s: number) {
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`
}

export { levelBadge }
