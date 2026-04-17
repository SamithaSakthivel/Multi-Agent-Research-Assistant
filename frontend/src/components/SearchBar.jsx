import './SearchBar.css'

export default function SearchBar({ query, setQuery, maxSources, setMaxSources, loading, onSubmit }) {
  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSubmit()
    }
  }

  return (
    <div className="searchbar">
      <div className="searchbar-input-row">
        <textarea
          className="searchbar-input"
          placeholder="Ask anything… e.g. 'What are the latest breakthroughs in quantum computing?'"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKey}
          rows={2}
          disabled={loading}
        />
        <button
          className={`searchbar-btn ${loading ? 'loading' : ''}`}
          onClick={onSubmit}
          disabled={loading || !query.trim()}
        >
          {loading ? (
            <span className="spinner" />
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>
      <div className="searchbar-options">
        <label className="sources-label">
          <span>Max sources:</span>
          <select
            value={maxSources}
            onChange={(e) => setMaxSources(Number(e.target.value))}
            disabled={loading}
            className="sources-select"
          >
            {[3, 5, 8, 10, 15].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </label>
        <span className="hint">Press Enter to search</span>
      </div>
    </div>
  )
}
