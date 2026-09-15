import { useState } from 'react'
import { RavenProvider } from './RavenContext'
import { DashboardPage } from './pages/DashboardPage'
import { ModelEvaluationPage } from './pages/ModelEvaluationPage'
import { DatasetPage } from './pages/DatasetPage'
import { ArchitecturePage } from './pages/ArchitecturePage'
import { PresentationMode } from './pages/PresentationMode'
import { ScenarioControl } from './components/ScenarioControl'
import { AgentPipelinePanel } from './components/AgentPipelinePanel'
import { EventTimeline } from './components/EventTimeline'
import {
  LayoutDashboard, Activity, Brain, Database,
  Network, FileText, Presentation, ChevronLeft, ChevronRight, Monitor
} from 'lucide-react'

const NAV = [
  { id: 'dashboard',    label: 'Dashboard',        icon: <LayoutDashboard size={14} /> },
  { id: 'scenarios',    label: 'Scenarios',         icon: <Activity size={14} /> },
  { id: 'agents',       label: 'Agents',            icon: <Network size={14} /> },
  { id: 'logs',         label: 'Event Log',         icon: <FileText size={14} /> },
  { id: 'models',       label: 'Model Evaluation',  icon: <Brain size={14} /> },
  { id: 'dataset',      label: 'Dataset',           icon: <Database size={14} /> },
  { id: 'architecture', label: 'Architecture',      icon: <Monitor size={14} /> },
  { id: 'presentation', label: 'Presentation Mode', icon: <Presentation size={14} /> },
]

function PageContent({ page }: { page: string }) {
  switch (page) {
    case 'dashboard':    return <DashboardPage />
    case 'scenarios':    return <div style={{ padding: 16 }}><ScenarioControl /></div>
    case 'agents':       return <div style={{ padding: 16 }}><AgentPipelinePanel /></div>
    case 'logs':         return <div style={{ padding: 16 }}><EventTimeline /></div>
    case 'models':       return <ModelEvaluationPage />
    case 'dataset':      return <DatasetPage />
    case 'architecture': return <ArchitecturePage />
    case 'presentation': return <PresentationMode />
    default:             return <DashboardPage />
  }
}

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [collapsed, setCollapsed] = useState(false)

  if (page === 'presentation') {
    return (
      <RavenProvider>
        <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
          <div style={{
            width: collapsed ? 48 : 180, background: '#070b14',
            borderRight: '1px solid var(--border)',
            display: 'flex', flexDirection: 'column',
            transition: 'width 0.2s',
            flexShrink: 0,
          }}>
            <button onClick={() => setPage('dashboard')}
              className="btn btn-ghost"
              style={{ margin: '8px', fontSize: 9, padding: '6px' }}>
              ← Back
            </button>
          </div>
          <div style={{ flex: 1, overflow: 'auto' }}>
            <PresentationMode />
          </div>
        </div>
      </RavenProvider>
    )
  }

  return (
    <RavenProvider>
      <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        {/* Sidebar */}
        <div style={{
          width: collapsed ? 48 : 196, background: '#070b14',
          borderRight: '1px solid var(--border)',
          display: 'flex', flexDirection: 'column',
          transition: 'width 0.2s', overflow: 'hidden',
          flexShrink: 0,
        }}>
          {/* Logo */}
          <div style={{
            padding: collapsed ? '14px 12px' : '14px 16px',
            borderBottom: '1px solid var(--border)',
            display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'space-between',
          }}>
            {!collapsed && (
              <div>
                <div style={{ fontSize: 16, fontWeight: 900, letterSpacing: '0.18em', color: '#e2e8f0' }}>RAVEN</div>
                <div style={{ fontSize: 8, color: '#0ea5e9', letterSpacing: '0.1em' }}>SIMULATION MODE</div>
              </div>
            )}
            <button
              onClick={() => setCollapsed(c => !c)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)', padding: 2 }}>
              {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
            </button>
          </div>

          {/* Nav */}
          <nav style={{ flex: 1, padding: '8px 6px', overflowY: 'auto' }}>
            {NAV.map(item => (
              <div key={item.id}
                className={`sidebar-link ${page === item.id ? 'active' : ''}`}
                onClick={() => setPage(item.id)}
                style={{ justifyContent: collapsed ? 'center' : 'flex-start' }}
                title={collapsed ? item.label : undefined}>
                {item.icon}
                {!collapsed && <span>{item.label}</span>}
              </div>
            ))}
          </nav>

          {/* Footer */}
          {!collapsed && (
            <div style={{ padding: '12px 14px', borderTop: '1px solid var(--border)', fontSize: 8, color: 'var(--text-dim)', lineHeight: 1.6 }}>
              v1.0.0 · Windows Host<br />
              RPi4 Not Connected<br />
              © 2026 RAVEN Project
            </div>
          )}
        </div>

        {/* Main content */}
        <div style={{ flex: 1, overflow: 'auto', background: 'var(--bg-base)' }}>
          <PageContent page={page} />
        </div>
      </div>
    </RavenProvider>
  )
}
