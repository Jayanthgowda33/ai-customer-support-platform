import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Conversations() {
  const [conversations, setConversations] = useState<any[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [reply, setReply] = useState('')

  useEffect(() => {
    api.listConversations().then(setConversations)
  }, [])

  useEffect(() => {
    if (selected) {
      api.getMessages(selected).then(setMessages)
    }
  }, [selected])

  async function sendReply() {
    if (!selected || !reply.trim()) return
    await api.agentReply(selected, reply)
    setReply('')
    api.getMessages(selected).then(setMessages)
    api.listConversations().then(setConversations)
  }

  return (
    <div>
      <h2>Conversations</h2>
      <div className="grid grid-2" style={{ gridTemplateColumns: '320px 1fr', alignItems: 'start' }}>
        <div className="card" style={{ maxHeight: 600, overflowY: 'auto' }}>
          {conversations.map((c) => (
            <div
              key={c.id}
              onClick={() => setSelected(c.id)}
              style={{
                padding: 10,
                borderRadius: 8,
                cursor: 'pointer',
                marginBottom: 4,
                background: selected === c.id ? 'var(--panel-2)' : 'transparent',
              }}
            >
              <div style={{ fontWeight: 600, fontSize: 13 }}>{c.customer_identifier}</div>
              <div style={{ fontSize: 12, color: 'var(--text-dim)' }}>
                {new Date(c.last_message_at).toLocaleString()}
              </div>
              {c.needs_human && <span className="badge open">Needs human</span>}
            </div>
          ))}
          {conversations.length === 0 && (
            <div style={{ color: 'var(--text-dim)', fontSize: 13 }}>No conversations yet.</div>
          )}
        </div>

        <div className="card" style={{ minHeight: 500, display: 'flex', flexDirection: 'column' }}>
          {!selected && <div style={{ color: 'var(--text-dim)' }}>Select a conversation</div>}
          {selected && (
            <>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
                {messages.map((m) => (
                  <div key={m.id} className={`bubble ${m.role}`}>
                    {m.content}
                    {m.intent && (
                      <div style={{ fontSize: 11, opacity: 0.7, marginTop: 4 }}>intent: {m.intent}</div>
                    )}
                  </div>
                ))}
              </div>
              <div className="chat-input-row" style={{ marginTop: 12, padding: 0 }}>
                <input
                  placeholder="Reply as agent..."
                  value={reply}
                  onChange={(e) => setReply(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendReply()}
                />
                <button onClick={sendReply}>Send</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
