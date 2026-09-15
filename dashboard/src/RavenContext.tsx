import { createContext, useContext, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { api } from './api'
import type { StatusResponse, SimResult, EventLog } from './api'

interface RavenState {
  status: StatusResponse | null
  latest: SimResult | null
  events: EventLog[]
  connected: boolean
  error: string | null
  startScenario: (sc: string) => Promise<void>
  stopScenario: () => Promise<void>
  resetScenario: () => Promise<void>
}

const Ctx = createContext<RavenState>({} as RavenState)

export function RavenProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [latest, setLatest] = useState<SimResult | null>(null)
  const [events, setEvents] = useState<EventLog[]>([])
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const esRef = useRef<EventSource | null>(null)

  // Poll status every 2 s
  useEffect(() => {
    const tick = async () => {
      try {
        const s = await api.status()
        setStatus(s)
        setConnected(true)
        setError(null)
      } catch (e) {
        setConnected(false)
        setError('Cannot reach RAVEN API. Is the backend running?')
      }
    }
    tick()
    const id = setInterval(tick, 2000)
    return () => clearInterval(id)
  }, [])

  // SSE for live result stream
  useEffect(() => {
    const es = new EventSource('/api/stream')
    esRef.current = es
    es.onmessage = (e) => {
      try {
        const result: SimResult = JSON.parse(e.data)
        setLatest(result)
      } catch { /* ignore bad frames */ }
    }
    es.onerror = () => setConnected(false)
    return () => es.close()
  }, [])

  // Poll events every 3 s
  useEffect(() => {
    const tick = async () => {
      try {
        const { events: evs } = await api.events(60)
        setEvents(evs.reverse())
      } catch { /* silent */ }
    }
    tick()
    const id = setInterval(tick, 3000)
    return () => clearInterval(id)
  }, [])

  const startScenario = async (sc: string) => {
    await api.startScenario(sc)
  }
  const stopScenario = async () => {
    await api.stopScenario()
  }
  const resetScenario = async () => {
    await api.resetScenario()
    setLatest(null)
    setEvents([])
  }

  return (
    <Ctx.Provider value={{ status, latest, events, connected, error, startScenario, stopScenario, resetScenario }}>
      {children}
    </Ctx.Provider>
  )
}

export const useRaven = () => useContext(Ctx)
