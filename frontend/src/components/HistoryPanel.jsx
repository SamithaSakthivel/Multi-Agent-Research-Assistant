import { useState, useEffect } from 'react'
import './HistoryPanel.css'

export default function HistoryPanel() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    fetch('/api/history')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((d) => setSessions(d.sessions || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="history-state">
      <span className="spinner-md" />
      <span>Loading history…</span>
    </div>
  )

  if (error) return (
    <div className="history-state error">⚠️ Could not load history: {error}</div>
  )

  if (!sessions.length) return (
    <div className="history-state">
      <span style={{ fontSize: '2.5rem' }}>📭</span>
      <span>No research sessions yet.</span>
      <span style={{ fontSize: '0.85rem', opacity: 0.6 }}>Run your first search to see history here.</span>
    </div>
  )

  return (
    <div className="history-panel">
      <h2 className="history-title">Research History</h2>
      <div className="history-list">
        {sessions.map((s) => (
          <div key={s.session_id} className="history-card">
            <div className="hcard-header" onClick={() => setExpanded(expanded === s.session_id ? null : s.session_id)}>
              <div className="hcard-left">
                <span className="hcard-query">{s.query}</span>
                <div className="hcard-meta">
                  <span>📄 {s.sources?.length ?? 0} sources</span>
                  <span>⏱ {s.elapsed_seconds}s</span>
                  <span>🗓 {new Date(s.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <span className="hcard-chevron">{expanded === s.session_id ? '▲' : '▼'}</span>
            </div>
            {expanded === s.session_id && (
              <div className="hcard-body">
                <p className="hcard-answer">{s.answer?.slice(0, 400)}…</p>
                {s.sources?.length > 0 && (
                  <div className="hcard-sources">
                    {s.sources.slice(0, 3).map((src, i) => (
                      <a key={i} href={src.url} target="_blank" rel="noopener noreferrer" className="hcard-source-link">
                        [{i + 1}] {src.title}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
