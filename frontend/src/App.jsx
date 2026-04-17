import { useState, useEffect, useRef } from 'react'
import socket from './socket'
import SearchBar from './components/SearchBar'
import AgentTimeline from './components/AgentTimeline'
import ResultPanel from './components/ResultPanel'
import HistoryPanel from './components/HistoryPanel'
import './App.css'

const API_BASE = `${import.meta.env.VITE_BACKEND_URL}/api`

export default function App() {
  const [query, setQuery] = useState('')
  const [maxSources, setMaxSources] = useState(5)
  const [loading, setLoading] = useState(false)
  const [events, setEvents] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [activeTab, setActiveTab] = useState('research') // 'research' | 'history'
  const sessionRef = useRef(null)

  // Socket.IO: listen for agent events
  useEffect(() => {
    socket.on('connect', () => console.log('[Socket] connected:', socket.id))
    socket.on('disconnect', () => console.log('[Socket] disconnected'))
    socket.on('agent_event', (event) => {
      setEvents((prev) => [...prev, event])
    })
    return () => {
      socket.off('agent_event')
      socket.off('connect')
      socket.off('disconnect')
    }
  }, [])

  const handleResearch = async () => {
    if (!query.trim()) return

    // Reset state
    setLoading(true)
    setEvents([])
    setResult(null)
    setError(null)

    // Generate a session id and join socket room
    const sid = crypto.randomUUID()
    setSessionId(sid)
    sessionRef.current = sid
    socket.emit('join_session', { session_id: sid })

    try {
      const res = await fetch(`${API_BASE}/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, max_sources: maxSources, session_id: sid }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `Server error ${res.status}`)
      }

      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">🔬</span>
            <span className="logo-text">ResearchAgent</span>
            <span className="logo-badge">AI</span>
          </div>
          <nav className="nav">
            <button
              className={`nav-btn ${activeTab === 'research' ? 'active' : ''}`}
              onClick={() => setActiveTab('research')}
            >Research</button>
            <button
              className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >History</button>
          </nav>
        </div>
      </header>

      <main className="main">
        {activeTab === 'research' ? (
          <>
            {/* Search section */}
            <section className="search-section">
              <h1 className="hero-title">Multi-Agent Research Assistant</h1>
              <p className="hero-sub">Powered by LangGraph · Tavily · Groq</p>
              <SearchBar
                query={query}
                setQuery={setQuery}
                maxSources={maxSources}
                setMaxSources={setMaxSources}
                loading={loading}
                onSubmit={handleResearch}
              />
            </section>

            {/* Error */}
            {error && (
              <div className="error-banner">
                <span>⚠️</span> {error}
              </div>
            )}

            {/* Agent Timeline */}
            {(loading || events.length > 0) && (
              <AgentTimeline events={events} loading={loading} />
            )}

            {/* Result */}
            {result && <ResultPanel result={result} />}
          </>
        ) : (
          <HistoryPanel />
        )}
      </main>
    </div>
  )
}
