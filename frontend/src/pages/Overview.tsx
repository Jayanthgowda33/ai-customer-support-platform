import { useEffect, useState } from 'react'
import { api, getSession } from '../lib/api'

export default function Overview() {
  const [stats, setStats] = useState<any>(null)
  const { org_slug } = getSession()

  useEffect(() => {
    api.getAnalytics().then(setStats).catch(() => {})
  }, [])

  const widgetUrl = `${window.location.origin}/widget/${org_slug}`

  return (
    <div>
      <h2>Overview</h2>
      <p style={{ color: 'var(--text-dim)' }}>
        Try the customer-facing chat here:{' '}
        <a href={widgetUrl} target="_blank" rel="noreferrer">
          {widgetUrl}
        </a>
      </p>

      {stats && (
        <div className="grid grid-4" style={{ marginTop: 20 }}>
          <div className="card">
            <div className="stat-value">{stats.total_conversations}</div>
            <div className="stat-label">Conversations</div>
          </div>
          <div className="card">
            <div className="stat-value">{stats.total_messages}</div>
            <div className="stat-label">Messages</div>
          </div>
          <div className="card">
            <div className="stat-value">{stats.open_tickets}</div>
            <div className="stat-label">Open tickets</div>
          </div>
          <div className="card">
            <div className="stat-value">
              {stats.satisfaction_rate != null ? `${Math.round(stats.satisfaction_rate * 100)}%` : '—'}
            </div>
            <div className="stat-label">Satisfaction rate</div>
          </div>
        </div>
      )}

      {stats?.top_intents?.length > 0 && (
        <div className="card" style={{ marginTop: 20 }}>
          <h3 style={{ marginTop: 0 }}>Top intents</h3>
          <table>
            <thead>
              <tr>
                <th>Intent</th>
                <th>Count</th>
              </tr>
            </thead>
            <tbody>
              {stats.top_intents.map((i: any) => (
                <tr key={i.intent}>
                  <td>{i.intent}</td>
                  <td>{i.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
