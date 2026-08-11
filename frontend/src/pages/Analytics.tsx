import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Analytics() {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    api.getAnalytics().then(setStats)
  }, [])

  if (!stats) return <div>Loading...</div>

  return (
    <div>
      <h2>Analytics</h2>
      <div className="grid grid-4">
        <Stat label="Total conversations" value={stats.total_conversations} />
        <Stat label="Total messages" value={stats.total_messages} />
        <Stat label="Total tickets" value={stats.total_tickets} />
        <Stat label="Open tickets" value={stats.open_tickets} />
        <Stat label="Handoff rate" value={`${Math.round(stats.handoff_rate * 100)}%`} />
        <Stat
          label="Satisfaction rate"
          value={stats.satisfaction_rate != null ? `${Math.round(stats.satisfaction_rate * 100)}%` : '—'}
        />
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3 style={{ marginTop: 0 }}>Intent breakdown</h3>
        {stats.top_intents.map((i: any) => (
          <div key={i.intent} style={{ marginBottom: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
              <span>{i.intent}</span>
              <span>{i.count}</span>
            </div>
            <div style={{ background: 'var(--panel-2)', height: 8, borderRadius: 4, marginTop: 4 }}>
              <div
                style={{
                  background: 'var(--accent)',
                  height: 8,
                  borderRadius: 4,
                  width: `${Math.min(100, i.count * 10)}%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: any }) {
  return (
    <div className="card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}
