import './AgentTimeline.css'

const AGENT_META = {
  orchestrator: { icon: '🧠', label: 'Orchestrator', color: '#6c63ff' },
  search:        { icon: '🔍', label: 'Search Agent', color: '#3b9eff' },
  summarizer:    { icon: '✍️', label: 'Summarizer',   color: '#4caf82' },
  citation:      { icon: '📎', label: 'Citations',    color: '#f0a060' },
}

const STATUS_ICON = {
  thinking: '💭',
  working:  '⚙️',
  done:     '✅',
  error:    '❌',
}

export default function AgentTimeline({ events, loading }) {
  // Deduplicate: keep the latest event per agent per status progression
  const grouped = {}
  for (const ev of events) {
    const key = ev.agent_name
    if (!grouped[key]) grouped[key] = []
    grouped[key].push(ev)
  }

  return (
    <div className="timeline">
      <div className="timeline-header">
        <span className="timeline-title">Agent Pipeline</span>
        {loading && <span className="live-badge">LIVE</span>}
      </div>
      <div className="timeline-body">
        {events.length === 0 && loading && (
          <div className="timeline-waiting">
            <span className="spinner-sm" /> Initialising agents…
          </div>
        )}
        {events.map((ev, i) => {
          const meta = AGENT_META[ev.agent_name] || { icon: '🤖', label: ev.agent_name, color: '#aaa' }
          return (
            <div key={i} className={`event-row ${ev.status}`}>
              <div className="event-agent" style={{ '--agent-color': meta.color }}>
                <span className="agent-icon">{meta.icon}</span>
                <span className="agent-label">{meta.label}</span>
              </div>
              <div className="event-content">
                <span className="status-icon">{STATUS_ICON[ev.status] || '•'}</span>
                <span className="event-msg">{ev.message}</span>
              </div>
              <span className="event-time">
                {new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
