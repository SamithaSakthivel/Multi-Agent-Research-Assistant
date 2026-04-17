import { useState } from 'react'
import './ResultPanel.css'

// Simple markdown renderer (avoid heavy dependencies)
function MarkdownContent({ text }) {
  // Convert markdown to basic HTML
  const html = text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    // headings
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // bold + italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // inline citations like [1]
    .replace(/\[(\d+)\]/g, '<sup class="cite">[$1]</sup>')
    // bullet list
    .replace(/^[-•] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
    // line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')

  return (
    <div
      className="md-content"
      dangerouslySetInnerHTML={{ __html: `<p>${html}</p>` }}
    />
  )
}

export default function ResultPanel({ result }) {
  const [activeTab, setActiveTab] = useState('answer')

  return (
    <div className="result-panel">
      {/* Meta bar */}
      <div className="result-meta">
        <span className="meta-query">"{result.query}"</span>
        <div className="meta-stats">
          <span>📄 {result.sources.length} sources</span>
          <span>⏱ {result.elapsed_seconds}s</span>
          <span>🔍 {result.sub_tasks.length} sub-tasks</span>
        </div>
      </div>

      {/* Tab bar */}
      <div className="result-tabs">
        {['answer', 'sources', 'citations', 'subtasks'].map((t) => (
          <button
            key={t}
            className={`rtab ${activeTab === t ? 'active' : ''}`}
            onClick={() => setActiveTab(t)}
          >
            {{ answer: '📝 Answer', sources: '🌐 Sources', citations: '📎 Citations', subtasks: '🔀 Sub-tasks' }[t]}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="result-body">
        {activeTab === 'answer' && (
          <MarkdownContent text={result.answer} />
        )}

        {activeTab === 'sources' && (
          <div className="sources-list">
            {result.sources.map((s, i) => (
              <a key={i} href={s.url} target="_blank" rel="noopener noreferrer" className="source-card">
                <div className="source-num">[{i + 1}]</div>
                <div className="source-info">
                  <div className="source-title">{s.title}</div>
                  <div className="source-url">{s.url}</div>
                  {s.snippet && <div className="source-snippet">{s.snippet.slice(0, 180)}…</div>}
                </div>
                <span className="source-arrow">↗</span>
              </a>
            ))}
          </div>
        )}

        {activeTab === 'citations' && (
          <div className="citations-list">
            {result.sources.map((s, i) => {
              const domain = (() => { try { return new URL(s.url).hostname.replace('www.', '') } catch { return s.url } })()
              const year = s.published_date ? s.published_date.slice(0, 4) : 'n.d.'
              return (
                <div key={i} className="citation-row">
                  <span className="cite-idx">[{i + 1}]</span>
                  <span className="cite-text">
                    {domain}. ({year}). <em>{s.title}</em>. <a href={s.url} target="_blank" rel="noopener noreferrer">{s.url}</a>
                  </span>
                </div>
              )
            })}
          </div>
        )}

        {activeTab === 'subtasks' && (
          <div className="subtasks-list">
            {result.sub_tasks.map((t, i) => (
              <div key={i} className="subtask-row">
                <span className="subtask-num">{i + 1}</span>
                <span>{t}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
