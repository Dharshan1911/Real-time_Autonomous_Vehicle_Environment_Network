// Central API client — all calls go through this module
const BASE = '/api'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`)
  return res.json()
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`)
  return res.json()
}

// ---- Types ----
export interface StatusResponse {
  mode: string
  hardware_connected: boolean
  models_loaded: boolean
  models_error: string | null
  scenario: string
  running: boolean
  tick: number
  uptime_seconds: number
  timestamp: string
  agents: Record<string, string>
}

export interface TelemetryPoint {
  timestamp: string
  scenario: string
  dht_temp: number | null
  dht_hum: number | null
  mpu_acc_x: number
  mpu_acc_y: number
  mpu_acc_z: number
  mpu_gyro_x: number
  mpu_gyro_y: number
  mpu_gyro_z: number
  ultra_dist: number | null
  pir_motion: number
  label: string
}

export interface SimResult {
  telemetry: TelemetryPoint
  time_series: {
    acc_mag: number[]
    gyro_mag: number[]
    temperature: (number | null)[]
    humidity: (number | null)[]
    distance: (number | null)[]
    pir: number[]
  }
  features: Record<string, number | null>
  models: {
    isolation_forest: { is_anomaly: boolean; score: number; threshold: number }
    xgboost: { predicted_class: string; confidence: number; class_probabilities: Record<string, number> }
    cnn: { predicted_class: string; confidence: number; latency_ms: number; class_probabilities: Record<string, number> }
  }
  fusion: { level: string; primary_fault: string; confidence: number; reasoning: string }
  decision: { action_type: string; target: string }
  recovery: { action_taken: string; success: boolean | null }
  verification: { status: string; message: string }
}

export interface EventLog {
  id: number
  timestamp: string
  level: string
  message: string
  agent: string
  fault: string
}

export interface ModelInfo {
  isolation_forest: {
    type: string; version: string; contamination: string; n_estimators: number
    threshold: number | null; size_kb: number | null
  }
  xgboost: {
    type: string; version: string; n_estimators: number; max_depth: number
    classes: string[]; test_accuracy: number; size_kb: number | null
  }
  cnn: {
    type: string; version: string; in_channels: number; num_classes: number
    test_accuracy: number; host_latency_ms: number; size_kb: number | null
  }
}

// ---- API calls ----
export const api = {
  status: () => get<StatusResponse>('/status'),
  latest: () => get<SimResult>('/latest'),
  history: () => get<{ history: TelemetryPoint[] }>('/history'),
  events: (limit = 50) => get<{ events: EventLog[] }>(`/events?limit=${limit}`),
  scenarios: () => get<{ scenarios: string[] }>('/scenarios'),
  modelInfo: () => get<ModelInfo>('/model_info'),
  datasetInfo: () => get<unknown>('/dataset_info'),

  startScenario: (scenario: string) => post('/scenario/start', { scenario }),
  stopScenario: () => post('/scenario/stop'),
  resetScenario: () => post('/scenario/reset'),
}
