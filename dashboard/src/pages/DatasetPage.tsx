import { useEffect, useState } from 'react'
import { api } from '../api'

export function DatasetPage() {
  const [info, setInfo] = useState<any>(null)
  useEffect(() => { api.datasetInfo().then(setInfo).catch(() => {}) }, [])

  const synth = info?.synthetic
  const uci = info?.uci_har

  return (
    <div style={{ padding: 16 }}>
      <div className="card-title" style={{ fontSize: 14, marginBottom: 16 }}>Datasets</div>

      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {/* Synthetic */}
        <div className="card" style={{ flex: '1 1 300px', borderColor: 'rgba(14,165,233,0.3)' }}>
          <div className="card-title">RAVEN Synthetic Telemetry</div>
          <div className="badge badge-info" style={{ marginBottom: 12 }}>PRIMARY DATASET</div>
          <p style={{ fontSize: 10, color: 'var(--text-secondary)', marginBottom: 14, lineHeight: 1.7 }}>
            {synth?.description ?? 'Parametric multi-variate sensor simulation at 50Hz across 8 fault scenarios.'}
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 14 }}>
            {[
              ['CSV Files', synth?.file_count ?? '--'],
              ['Sample Rate', `${synth?.sampling_rate_hz ?? 50} Hz`],
              ['Window Size', `${synth?.window_size ?? 128} samples`],
              ['Fault Classes', 8],
            ].map(([l, v]) => (
              <div key={l as string} style={{ padding: '8px 10px', background: 'var(--bg-card-alt)', borderRadius: 5 }}>
                <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 2 }}>{l}</div>
                <div style={{ fontWeight: 700, fontSize: 13 }}>{v}</div>
              </div>
            ))}
          </div>
          <div>
            <div style={{ fontSize: 9, color: 'var(--text-secondary)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Raw Channels (10)</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {(synth?.features ?? ['dht_temp','dht_hum','mpu_acc_x','mpu_acc_y','mpu_acc_z','mpu_gyro_x','mpu_gyro_y','mpu_gyro_z','ultra_dist','pir_motion']).map((f: string) => (
                <span key={f} className="badge badge-info" style={{ fontSize: 8 }}>{f}</span>
              ))}
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 9, color: 'var(--text-secondary)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Fault Classes (8)</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {(synth?.classes ?? ['NORMAL','OVERHEATING','IMPACT_LIKE_EVENT','HIGH_VIBRATION','OBSTACLE_APPROACH','SENSOR_STUCK','SENSOR_DROPOUT','MULTI_SENSOR_ANOMALY']).map((c: string) => (
                <span key={c} className={`badge ${c === 'NORMAL' ? 'badge-normal' : 'badge-warning'}`} style={{ fontSize: 8 }}>{c}</span>
              ))}
            </div>
          </div>
        </div>

        {/* UCI HAR */}
        <div className="card" style={{ flex: '1 1 300px', borderColor: 'rgba(100,116,139,0.3)' }}>
          <div className="card-title">UCI Human Activity Recognition</div>
          <div className="badge badge-offline" style={{ marginBottom: 12 }}>AUXILIARY — ARCHITECTURE EXPLORATION ONLY</div>
          <p style={{ fontSize: 10, color: 'var(--text-secondary)', marginBottom: 14, lineHeight: 1.7 }}>
            Used to verify the 1D CNN architecture can learn from real-world 6-axis IMU data before committing to the architecture.
            <br /><br />
            <strong style={{ color: '#ef4444' }}>NOT the primary RAVEN vehicle-fault dataset.</strong>{' '}
            No metrics are reported from UCI HAR in the final evaluation.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 14 }}>
            {[
              ['Sample Rate', `${uci?.sampling_rate_hz ?? 50} Hz`],
              ['Window Size', `${uci?.window_size ?? 128} samples`],
              ['Domain', 'Human Activity'],
              ['Role in RAVEN', 'Architecture only'],
            ].map(([l, v]) => (
              <div key={l as string} style={{ padding: '8px 10px', background: 'var(--bg-card-alt)', borderRadius: 5 }}>
                <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 2 }}>{l}</div>
                <div style={{ fontWeight: 700, fontSize: 13 }}>{v}</div>
              </div>
            ))}
          </div>
          <div style={{ padding: '10px', background: 'rgba(71,85,105,0.1)', border: '1px solid rgba(71,85,105,0.3)', borderRadius: 6, fontSize: 10, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            UCI HAR was used during early development to confirm the 1D CNN architecture could extract kinetic patterns from real-world 50Hz IMU data.
            It was not used for training or evaluation of RAVEN's fault detection pipeline.
          </div>
        </div>
      </div>
    </div>
  )
}
