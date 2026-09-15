import { useRaven } from '../RavenContext'
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts'

function ConfidenceBar({ value, color }: { value: number; color: string }) {
  return (
    <div style={{ flex: 1 }}>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${(value * 100).toFixed(0)}%`, background: color }} />
      </div>
      <div style={{ fontSize: 9, color: 'var(--text-secondary)', marginTop: 2, textAlign: 'right' }}>
        {(value * 100).toFixed(0)}%
      </div>
    </div>
  )
}

function ModelCard({
  title, result, confidence, detail, color, anomaly
}: {
  title: string; result: string; confidence: number; detail?: string; color: string; anomaly?: boolean
}) {
  return (
    <div className="card" style={{ flex: 1, minWidth: 0, borderColor: anomaly ? 'rgba(239,68,68,0.3)' : 'var(--border)' }}>
      <div className="card-title">{title}</div>
      <div style={{ fontSize: 20, fontWeight: 800, color, marginBottom: 4, letterSpacing: '0.05em' }}>{result}</div>
      {detail && <div style={{ fontSize: 10, color: 'var(--text-dim)', marginBottom: 8 }}>{detail}</div>}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 9, color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>CONF</span>
        <ConfidenceBar value={confidence} color={color} />
        <span style={{ fontSize: 13, fontWeight: 700, color }}>{(confidence * 100).toFixed(0)}%</span>
      </div>
    </div>
  )
}

const CLASS_LABELS = [
  'NORMAL','OVERHEATING','IMPACT','HIGH_VIB','OBSTACLE','STUCK','DROPOUT','MULTI'
]
const FULL_CLASS = [
  'NORMAL','OVERHEATING','IMPACT_LIKE_EVENT','HIGH_VIBRATION',
  'OBSTACLE_APPROACH','SENSOR_STUCK','SENSOR_DROPOUT','MULTI_SENSOR_ANOMALY'
]

export function AIAnalysisPanel() {
  const { latest } = useRaven()
  const m = latest?.models

  const isoAnomaly = m?.isolation_forest.is_anomaly ?? false
  const isoScore = m?.isolation_forest.score ?? 0
  const isoThresh = m?.isolation_forest.threshold ?? -0.55

  const xgbClass = m?.xgboost.predicted_class ?? '--'
  const xgbConf = m?.xgboost.confidence ?? 0

  const cnnClass = m?.cnn.predicted_class ?? '--'
  const cnnConf = m?.cnn.confidence ?? 0
  const cnnLatency = m?.cnn.latency_ms ?? 0

  // Radar data for XGBoost class probabilities
  const xgbProbs = m?.xgboost.class_probabilities
  const radarData = xgbProbs
    ? FULL_CLASS.map((fc, i) => ({ subject: CLASS_LABELS[i], A: Math.round((xgbProbs[fc] ?? 0) * 100) }))
    : []

  const fusionLevel = latest?.fusion?.level ?? 'NORMAL'
  const fusionColor = {
    NORMAL: '#22c55e', SUSPICIOUS: '#eab308', WARNING: '#f97316', CRITICAL: '#ef4444'
  }[fusionLevel] ?? '#0ea5e9'

  return (
    <div>
      <div className="card-title">AI Analysis</div>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
        <ModelCard
          title="Isolation Forest (Unsupervised)"
          result={isoAnomaly ? 'ANOMALY' : 'NORMAL'}
          confidence={isoAnomaly ? Math.min(1, Math.abs(isoScore / isoThresh)) : 0.95}
          detail={`Score: ${isoScore.toFixed(3)} / Threshold: ${isoThresh.toFixed(3)}`}
          color={isoAnomaly ? '#ef4444' : '#22c55e'}
          anomaly={isoAnomaly}
        />
        <ModelCard
          title="XGBoost (Tabular Classifier)"
          result={xgbClass}
          confidence={xgbConf}
          color={xgbClass === 'NORMAL' ? '#22c55e' : '#f97316'}
          anomaly={xgbClass !== 'NORMAL'}
        />
        <ModelCard
          title="1D CNN (Temporal)"
          result={cnnClass}
          confidence={cnnConf}
          detail={`ONNX inference: ${cnnLatency.toFixed(2)} ms (host CPU)`}
          color={cnnClass === 'NORMAL' ? '#22c55e' : '#a855f7'}
          anomaly={cnnClass !== 'NORMAL'}
        />
      </div>

      {/* Radar + Fusion */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        {/* XGBoost probability radar */}
        <div className="card" style={{ flex: '1 1 260px' }}>
          <div className="card-title">XGBoost — Class Probability Distribution</div>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData} margin={{ top: 4, right: 30, left: 30, bottom: 4 }}>
              <PolarGrid stroke="#1e2d45" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 9 }} />
              <Tooltip
                contentStyle={{ background: '#0f172a', border: '1px solid #1e2d45', fontSize: 10, borderRadius: 6 }}
                formatter={(v: any) => [`${v}%`, 'Probability']}
              />
              <Radar dataKey="A" stroke="#f97316" fill="#f97316" fillOpacity={0.2} strokeWidth={1.5} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Fusion card */}
        <div className="card" style={{ flex: '1 1 260px', borderColor: fusionColor + '40' }}>
          <div className="card-title">AI Fusion Result</div>
          <div style={{ textAlign: 'center', padding: '12px 0' }}>
            <div style={{ fontSize: 32, fontWeight: 900, color: fusionColor, letterSpacing: '0.05em', marginBottom: 4 }}>
              {fusionLevel}
            </div>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>
              {latest?.fusion?.primary_fault ?? '--'}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 12 }}>
              <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>CONFIDENCE</span>
              <span style={{ fontSize: 16, fontWeight: 700, color: fusionColor }}>
                {((latest?.fusion?.confidence ?? 0) * 100).toFixed(0)}%
              </span>
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-secondary)', maxWidth: 280, margin: '0 auto', lineHeight: 1.6 }}>
              {latest?.fusion?.reasoning ?? 'Awaiting simulation data...'}
            </div>
          </div>
          <div style={{ marginTop: 12, padding: '8px 10px', background: 'rgba(14,165,233,0.06)', border: '1px solid rgba(14,165,233,0.15)', borderRadius: 6 }}>
            <div style={{ fontSize: 9, color: 'var(--text-dim)' }}>
              AI Fusion combines anomaly detection (Isolation Forest), fault classification (XGBoost),
              and temporal pattern analysis (1D CNN) to determine system health.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
