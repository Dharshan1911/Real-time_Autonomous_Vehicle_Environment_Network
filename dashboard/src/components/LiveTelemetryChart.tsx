import { useRaven } from '../RavenContext'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine
} from 'recharts'
import { useState } from 'react'

type Metric = 'acc_mag' | 'gyro_mag' | 'temperature' | 'humidity' | 'distance' | 'pir'

const METRICS: { key: Metric; label: string; unit: string; color: string; ref?: number }[] = [
  { key: 'acc_mag',     label: 'Accel Magnitude', unit: 'g',   color: '#0ea5e9', ref: 1.0 },
  { key: 'gyro_mag',   label: 'Gyro Magnitude',  unit: '°/s', color: '#a855f7' },
  { key: 'temperature',label: 'Temperature',      unit: '°C',  color: '#f97316', ref: 25 },
  { key: 'humidity',   label: 'Humidity',         unit: '%',   color: '#22c55e' },
  { key: 'distance',   label: 'Distance',         unit: 'cm',  color: '#eab308' },
  { key: 'pir',        label: 'PIR Activity',     unit: '',    color: '#ec4899' },
]

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#0f172a', border: '1px solid #1e2d45', borderRadius: 6, padding: '6px 10px', fontSize: 11 }}>
      <div style={{ color: payload[0].color, fontWeight: 700 }}>
        {Number(payload[0].value).toFixed(3)}
      </div>
    </div>
  )
}

export function LiveTelemetryChart() {
  const { latest } = useRaven()
  const [active, setActive] = useState<Metric>('acc_mag')

  const meta = METRICS.find(m => m.key === active)!
  const raw = latest?.time_series?.[active] ?? []
  const data = raw.map((v, i) => ({ i, v: v === null ? undefined : v }))

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
        <div className="card-title" style={{ margin: 0 }}>Live Telemetry — 128-sample Window</div>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {METRICS.map(m => (
            <button key={m.key}
              onClick={() => setActive(m.key)}
              style={{
                padding: '3px 8px', borderRadius: 4, fontSize: 10, cursor: 'pointer',
                background: active === m.key ? m.color + '30' : 'transparent',
                border: `1px solid ${active === m.key ? m.color : 'var(--border)'}`,
                color: active === m.key ? m.color : 'var(--text-dim)',
                fontWeight: active === m.key ? 700 : 400,
                transition: 'all 0.15s',
              }}>{m.label}</button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 12 }}>
        <span style={{ fontSize: 28, fontWeight: 800, color: meta.color }}>
          {data.length ? (data[data.length - 1]?.v?.toFixed(3) ?? 'NaN') : '--'}
        </span>
        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{meta.unit}</span>
      </div>

      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="i" tick={false} axisLine={false} />
          <YAxis tick={{ fontSize: 9 }} />
          <Tooltip content={<CustomTooltip />} />
          {meta.ref !== undefined && (
            <ReferenceLine y={meta.ref} stroke={meta.color} strokeDasharray="4 4" strokeOpacity={0.4} />
          )}
          <Line type="monotone" dataKey="v" stroke={meta.color} strokeWidth={1.5}
            dot={false} connectNulls={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 9, color: 'var(--text-dim)', marginTop: 4, textAlign: 'right' }}>
        32 points sampled from 128-sample window (50 Hz) — simulation data
      </div>
    </div>
  )
}
