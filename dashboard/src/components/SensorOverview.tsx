import { useRaven } from '../RavenContext'
import { Thermometer, Activity, Radar, Eye } from 'lucide-react'

function SensorCard({ title, icon, children, status }: {
  title: string; icon: React.ReactNode; children: React.ReactNode; status: 'ok' | 'warn' | 'error' | 'unknown'
}) {
  const border = {
    ok: 'rgba(34,197,94,0.3)',
    warn: 'rgba(249,115,22,0.3)',
    error: 'rgba(239,68,68,0.4)',
    unknown: 'var(--border)',
  }[status]
  const dot = {
    ok: '#22c55e', warn: '#f97316', error: '#ef4444', unknown: '#64748b'
  }[status]

  return (
    <div className="card" style={{ borderColor: border, flex: '1 1 200px', minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ color: 'var(--accent)' }}>{icon}</div>
          <span className="card-title" style={{ margin: 0 }}>{title}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
          <div className="pulse-dot" style={{ background: dot }} />
          <span style={{ fontSize: 9, color: dot, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            {status === 'ok' ? 'Live' : status === 'unknown' ? 'No Data' : status === 'error' ? 'Dropout' : 'Warning'}
          </span>
        </div>
      </div>
      {children}
    </div>
  )
}

function Row({ label, value, unit }: { label: string; value: string | number | null; unit?: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 6 }}>
      <span style={{ color: 'var(--text-dim)', fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{label}</span>
      <span style={{ fontWeight: 700, fontSize: 13 }}>
        {value === null ? <span style={{ color: '#ef4444' }}>NaN</span> : value}
        {unit && value !== null && <span style={{ color: 'var(--text-secondary)', fontSize: 10, marginLeft: 3 }}>{unit}</span>}
      </span>
    </div>
  )
}

function accMag(t: { mpu_acc_x: number; mpu_acc_y: number; mpu_acc_z: number }) {
  return Math.sqrt(t.mpu_acc_x ** 2 + t.mpu_acc_y ** 2 + t.mpu_acc_z ** 2).toFixed(3)
}

export function SensorOverview() {
  const { latest } = useRaven()
  const t = latest?.telemetry

  const dhtStatus = !t ? 'unknown' : t.dht_temp === null ? 'error' : (t.dht_temp > 40 ? 'warn' : 'ok')
  const mpuStatus = !t ? 'unknown' : 'ok'
  const ultraStatus = !t ? 'unknown' : t.ultra_dist === null ? 'error' : (t.ultra_dist < 30 ? 'warn' : 'ok')
  const pirStatus = !t ? 'unknown' : t.pir_motion ? 'warn' : 'ok'

  return (
    <div>
      <div className="card-title">Sensor Overview</div>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <SensorCard title="DHT11" icon={<Thermometer size={14} />} status={dhtStatus}>
          <Row label="Temperature" value={t?.dht_temp ?? null} unit="°C" />
          <Row label="Humidity" value={t?.dht_hum ?? null} unit="%" />
        </SensorCard>

        <SensorCard title="MPU6050" icon={<Activity size={14} />} status={mpuStatus}>
          <Row label="Acc X" value={t?.mpu_acc_x?.toFixed(3) ?? null} unit="g" />
          <Row label="Acc Y" value={t?.mpu_acc_y?.toFixed(3) ?? null} unit="g" />
          <Row label="Acc Z" value={t?.mpu_acc_z?.toFixed(3) ?? null} unit="g" />
          <Row label="|Acc|" value={t ? accMag(t) : null} unit="g" />
          <Row label="Gyro X" value={t?.mpu_gyro_x?.toFixed(2) ?? null} unit="°/s" />
          <Row label="Gyro Y" value={t?.mpu_gyro_y?.toFixed(2) ?? null} unit="°/s" />
          <Row label="Gyro Z" value={t?.mpu_gyro_z?.toFixed(2) ?? null} unit="°/s" />
        </SensorCard>

        <SensorCard title="HC-SR04" icon={<Radar size={14} />} status={ultraStatus}>
          <Row label="Distance" value={t?.ultra_dist ?? null} unit="cm" />
          {t?.ultra_dist !== null && t?.ultra_dist !== undefined && (
            <div style={{ marginTop: 8 }}>
              <div className="progress-bar">
                <div className="progress-fill" style={{
                  width: `${Math.min(100, ((t.ultra_dist) / 400) * 100)}%`,
                  background: t.ultra_dist < 30 ? '#ef4444' : t.ultra_dist < 80 ? '#f97316' : '#22c55e',
                }} />
              </div>
              <div style={{ fontSize: 9, color: 'var(--text-dim)', marginTop: 3 }}>0 — 400 cm</div>
            </div>
          )}
        </SensorCard>

        <SensorCard title="PIR" icon={<Eye size={14} />} status={pirStatus}>
          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <div className="metric-value" style={{ color: t?.pir_motion ? '#f97316' : '#22c55e' }}>
              {t ? (t.pir_motion ? 'MOTION' : 'CLEAR') : '--'}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-secondary)', marginTop: 4 }}>Motion Detection</div>
          </div>
        </SensorCard>
      </div>
    </div>
  )
}
