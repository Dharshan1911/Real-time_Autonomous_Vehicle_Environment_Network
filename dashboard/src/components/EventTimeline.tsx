import { useRaven } from '../RavenContext'
import type { EventLog } from '../api'

function levelStyle(level: string): { bg: string; color: string; label: string } {
  return {
    CRITICAL:  { bg: 'rgba(239,68,68,0.12)',  color: '#ef4444', label: 'CRIT' },
    WARNING:   { bg: 'rgba(249,115,22,0.12)', color: '#f97316', label: 'WARN' },
    SUSPICIOUS:{ bg: 'rgba(234,179,8,0.12)',  color: '#eab308', label: 'SUSP' },
    INFO:      { bg: 'rgba(14,165,233,0.08)',  color: '#0ea5e9', label: 'INFO' },
    NORMAL:    { bg: 'rgba(34,197,94,0.08)',   color: '#22c55e', label: 'NORM' },
  }[level?.toUpperCase()] ?? { bg: 'rgba(100,116,139,0.1)', color: '#64748b', label: level?.slice(0,4) ?? '---' }
}

function EventRow({ ev }: { ev: EventLog }) {
  const ts = new Date(ev.timestamp)
  const time = ts.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  const style = levelStyle(ev.level)
  return (
    <div style={{
      display: 'flex', gap: 10, alignItems: 'flex-start',
      padding: '6px 10px', borderRadius: 4, marginBottom: 3,
      background: style.bg, borderLeft: `2px solid ${style.color}`,
      fontSize: 10,
    }}>
      <span style={{ color: 'var(--text-dim)', whiteSpace: 'nowrap', fontFamily: 'monospace', minWidth: 64 }}>{time}</span>
      <span style={{ color: style.color, fontWeight: 700, minWidth: 32, fontSize: 9 }}>{style.label}</span>
      <span style={{ color: 'var(--text-secondary)', minWidth: 80 }}>{ev.agent}</span>
      <span style={{ color: 'var(--text-primary)', flex: 1 }}>{ev.message}</span>
    </div>
  )
}

export function EventTimeline() {
  const { events } = useRaven()

  return (
    <div className="card" style={{ height: 320, display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <div className="card-title" style={{ margin: 0 }}>Event Timeline</div>
        <span style={{ fontSize: 9, color: 'var(--text-dim)' }}>{events.length} events</span>
      </div>
      <div style={{ overflow: 'auto', flex: 1 }}>
        {events.length === 0
          ? <div style={{ color: 'var(--text-dim)', fontSize: 10, padding: '20px 0', textAlign: 'center' }}>
              Start a scenario to begin recording events.
            </div>
          : events.map((ev, i) => <EventRow key={`${ev.id}-${i}`} ev={ev} />)
        }
      </div>
    </div>
  )
}
