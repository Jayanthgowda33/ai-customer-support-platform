import { useEffect, useState } from 'react'
import { api } from '../lib/api'

const STATUSES = ['open', 'in_progress', 'resolved', 'closed']

export default function Tickets() {
  const [tickets, setTickets] = useState<any[]>([])
  const [filter, setFilter] = useState('')

  function refresh() {
    api.listTickets(filter || undefined).then(setTickets)
  }

  useEffect(() => {
    refresh()
  }, [filter])

  async function updateStatus(id: string, status: string) {
    await api.updateTicket(id, { status })
    refresh()
  }

  return (
    <div>
      <h2>Tickets</h2>
      <div style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
        <button className={filter === '' ? '' : 'secondary'} onClick={() => setFilter('')}>
          All
        </button>
        {STATUSES.map((s) => (
          <button key={s} className={filter === s ? '' : 'secondary'} onClick={() => setFilter(s)}>
            {s}
          </button>
        ))}
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Subject</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Created</th>
              <th>Change status</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((t) => (
              <tr key={t.id}>
                <td>{t.subject}</td>
                <td>{t.priority}</td>
                <td>
                  <span className={`badge ${t.status}`}>{t.status}</span>
                </td>
                <td>{new Date(t.created_at).toLocaleString()}</td>
                <td>
                  <select value={t.status} onChange={(e) => updateStatus(t.id, e.target.value)}>
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
            {tickets.length === 0 && (
              <tr>
                <td colSpan={5} style={{ color: 'var(--text-dim)' }}>
                  No tickets.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
