import { useEffect, useRef, useState } from 'react'
import ScriptCard from './components/ScriptCard'

function App() {
  const [scripts, setScripts] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [expandedId, setExpandedId] = useState(null)
  const [loadingScriptId, setLoadingScriptId] = useState(null)
  const [scriptContent, setScriptContent] = useState({})
  const [toast, setToast] = useState(null)
  const [error, setError] = useState(null)
  const [sessions, setSessions] = useState([])
  const [formUrl, setFormUrl] = useState('')
  const [formMode, setFormMode] = useState('setup')
  const [formDuration, setFormDuration] = useState(60)
  const [isLaunching, setIsLaunching] = useState(false)
  const apiRef = useRef(null)
  const toastTimer = useRef(null)

  useEffect(() => {
    apiRef.current = window.api?.gaze ?? null

    if (!apiRef.current) {
      setError('The gaze script bridge is unavailable. Restart the app and try again.')
      setIsLoading(false)
      return () => {}
    }

    const loadScripts = async () => {
      try {
        const list = await apiRef.current.listScripts()
        setScripts(list)
      } catch (err) {
        console.error('[renderer] Failed to load scripts', err)
        setError(err?.message || 'Unable to load scripts. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }

    const unsubscribe = apiRef.current.onSessionEvent?.((sessionEvent) => {
      if (!sessionEvent?.sessionId) return

      setSessions((prev) => {
        const next = [...prev]
        const index = next.findIndex((item) => item.sessionId === sessionEvent.sessionId)
        const baseInfo =
          index >= 0
            ? next[index]
            : {
                sessionId: sessionEvent.sessionId,
                mode: sessionEvent.mode || 'setup',
                url: sessionEvent.url || '',
                status: 'Created',
                profile: null,
                profilePath: null
              }

        let status = baseInfo.status
        let result = baseInfo.result
        let message = baseInfo.message
        let profile = baseInfo.profile
        let profilePath = baseInfo.profilePath

        switch (sessionEvent.type) {
          case 'created':
            status = 'Opening browser window'
            break
          case 'navigated':
            status = 'Page loaded, injecting script'
            baseInfo.url = sessionEvent.url || baseInfo.url
            break
          case 'script-ready':
            status =
              baseInfo.mode === 'setup'
                ? 'Setup script ready. Use the new window to label elements.'
                : 'Play script ready. Tracking will begin shortly.'
            break
          case 'running':
            status = `Running play session (${Math.round((sessionEvent.durationMs || 0) / 1000)}s)`
            break
          case 'profile-saved':
            status = 'Profile saved to disk'
            profile = sessionEvent.profile || profile
            profilePath = sessionEvent.profilePath || profilePath
            break
          case 'completed':
            status = 'Play session finished'
            result = sessionEvent.result
            break
          case 'error':
            status = 'Error'
            message = sessionEvent.message
            break
          case 'closed':
            status = 'Window closed'
            break
          default:
            break
        }

        const updated = {
          ...baseInfo,
          mode: sessionEvent.mode || baseInfo.mode,
          status,
          result,
          message,
          profile,
          profilePath
        }

        if (index >= 0) {
          next[index] = updated
        } else {
          next.unshift(updated)
        }

        return next
      })
    })

    loadScripts()

    return () => {
      if (toastTimer.current) {
        clearTimeout(toastTimer.current)
      }
      if (typeof unsubscribe === 'function') {
        unsubscribe()
      }
    }
  }, [])

  const showToast = (type, text) => {
    if (toastTimer.current) {
      clearTimeout(toastTimer.current)
    }
    setToast({ type, text })
    toastTimer.current = setTimeout(() => setToast(null), 2400)
  }

  const handleToggle = async (id) => {
    if (expandedId === id) {
      setExpandedId(null)
      return
    }

    if (!apiRef.current) {
      return
    }

    if (!scriptContent[id]) {
      setLoadingScriptId(id)
      try {
        const data = await apiRef.current.getScript(id)
        setScriptContent((prev) => ({ ...prev, [id]: data.code }))
        setExpandedId(id)
      } catch (err) {
        console.error('[renderer] Failed to fetch script', err)
        showToast('error', err?.message || 'Unable to load the script body.')
      } finally {
        setLoadingScriptId(null)
      }
    } else {
      setExpandedId(id)
    }
  }

  const handleCopy = async (id) => {
    if (!apiRef.current) {
      return
    }

    try {
      await apiRef.current.copyScript(id)
      const script = scripts.find((item) => item.id === id)
      showToast('success', `${script?.title || 'Script'} copied to clipboard.`)
    } catch (err) {
      console.error('[renderer] Failed to copy script', err)
      showToast('error', err?.message || 'Unable to copy the script.')
    }
  }

  const handleLaunch = async (event) => {
    event.preventDefault()
    if (!apiRef.current) {
      return
    }
    const trimmedUrl = formUrl.trim()
    if (!trimmedUrl) {
      showToast('error', 'Please enter a target URL.')
      return
    }

    setIsLaunching(true)
    try {
      await apiRef.current.runScript({
        url: trimmedUrl,
        mode: formMode,
        durationSeconds: formMode === 'play' ? Number(formDuration) : undefined
      })
      showToast('success', 'Session launched in a new window.')
    } catch (err) {
      console.error('[renderer] Failed to launch session', err)
      showToast('error', err?.message || 'Unable to start the session.')
    } finally {
      setIsLaunching(false)
    }
  }

  const renderSessionResult = (session) => {
    const sections = []

    if (session.result) {
      const { countsByRank, ranksBySelector, occurrencesBySelector } = session.result
      sections.push(
        <div className="session-result__section" key="counts">
          <h4>Counts by rank</h4>
          <ul>
            {Object.entries(countsByRank || {}).map(([key, value]) => (
              <li key={key}>
                <span>{key.toUpperCase()}</span>
                <span>{value}</span>
              </li>
            ))}
          </ul>
        </div>
      )
      sections.push(
        <div className="session-result__section" key="occurrences">
          <h4>Occurrences by selector</h4>
          <pre>{JSON.stringify(occurrencesBySelector ?? {}, null, 2)}</pre>
        </div>
      )
      sections.push(
        <div className="session-result__section" key="ranks">
          <h4>Ranks by selector</h4>
          <pre>{JSON.stringify(ranksBySelector ?? {}, null, 2)}</pre>
        </div>
      )
    }

    if (session.profilePath) {
      sections.push(
        <div className="session-result__section" key="profile-path">
          <h4>Profile path</h4>
          <code className="session-result__path">{session.profilePath}</code>
        </div>
      )
    }

    if (session.profile?.ranks) {
      sections.push(
        <div className="session-result__section" key="profile-ranks">
          <h4>Saved ranks</h4>
          <pre>{JSON.stringify(session.profile.ranks, null, 2)}</pre>
        </div>
      )
    }

    if (sections.length === 0) {
      return null
    }

    return <div className="session-result">{sections}</div>
  }

  return (
    <div className="page">
      <header className="page__header">
        <h1>Browser Console Scripts</h1>
        <p>Start with these gaze tools to configure a page or replay a saved profile.</p>
      </header>
      <div className="page__hint">
        Paste the script you need into the DevTools console of the page you are working with, or launch a session directly below.
      </div>
      <section className="session-panel">
        <form className="session-form" onSubmit={handleLaunch}>
          <div className="form-field">
            <label htmlFor="gaze-url">Target URL</label>
            <input
              id="gaze-url"
              type="url"
              placeholder="https://example.com"
              value={formUrl}
              onChange={(e) => setFormUrl(e.target.value)}
              required
            />
          </div>
          <div className="form-field">
            <span className="form-label">Session type</span>
            <div className="form-options">
              <label>
                <input
                  type="radio"
                  name="gaze-mode"
                  value="setup"
                  checked={formMode === 'setup'}
                  onChange={() => setFormMode('setup')}
                />
                <span>Setup</span>
              </label>
              <label>
                <input
                  type="radio"
                  name="gaze-mode"
                  value="play"
                  checked={formMode === 'play'}
                  onChange={() => setFormMode('play')}
                />
                <span>Play</span>
              </label>
            </div>
          </div>
          {formMode === 'play' ? (
            <div className="form-field">
              <label htmlFor="gaze-duration">Play duration (seconds)</label>
              <input
                id="gaze-duration"
                type="number"
                min="1"
                value={formDuration}
                onChange={(e) => setFormDuration(e.target.value)}
                required
              />
            </div>
          ) : null}
          <div className="form-actions">
            <button type="submit" className="btn btn--primary" disabled={isLaunching}>
              {isLaunching ? 'Launching...' : 'Launch session'}
            </button>
          </div>
        </form>
        <div className="session-log">
          <h3>Recent sessions</h3>
          {sessions.length === 0 ? (
            <div className="session-log__empty">No sessions launched yet.</div>
          ) : (
            sessions.map((session) => (
              <div className="session-log__item" key={session.sessionId}>
                <div className="session-log__meta">
                  <div>
                    <span className="session-badge">{session.mode}</span>
                    <span className="session-url">{session.url}</span>
                  </div>
                  <span className="session-status">{session.status}</span>
                </div>
                {session.message ? <div className="session-message">{session.message}</div> : null}
                {renderSessionResult(session)}
              </div>
            ))
          )}
        </div>
      </section>
      {toast ? <div className={`notice notice--${toast.type}`}>{toast.text}</div> : null}
      {error ? <div className="notice notice--error">{error}</div> : null}
      {isLoading ? (
        <div className="page__loading">Loading scripts...</div>
      ) : (
        <div className="script-list">
          {scripts.map((script) => (
            <ScriptCard
              key={script.id}
              meta={script}
              isExpanded={expandedId === script.id}
              code={scriptContent[script.id] ?? ''}
              loading={loadingScriptId === script.id}
              onToggle={handleToggle}
              onCopy={handleCopy}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default App
