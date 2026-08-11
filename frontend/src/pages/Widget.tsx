import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../lib/api'

interface ChatMessage {
  id: string
  role: 'customer' | 'ai' | 'agent'
  content: string
  citations?: { document_title: string; snippet: string }[]
  needs_human?: boolean
}

export default function Widget() {
  const { orgSlug } = useParams()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<string | undefined>()
  const [customerId] = useState(() => `guest_${Math.random().toString(36).slice(2, 10)}`)
  const [loading, setLoading] = useState(false)
  const bodyRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight })
  }, [messages])

  async function send() {
    if (!input.trim() || !orgSlug) return
    const userMsg: ChatMessage = { id: `local-${Date.now()}`, role: 'customer', content: input }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setLoading(true)
    try {
      const res = await api.sendChatMessage({
        org_slug: orgSlug,
        customer_identifier: customerId,
        message: userMsg.content,
        conversation_id: conversationId,
      })
      setConversationId(res.conversation_id)
      setMessages((m) => [
        ...m,
        {
          id: res.message_id,
          role: 'ai',
          content: res.response,
          citations: res.citations,
          needs_human: res.needs_human,
        },
      ])
    } catch (e: any) {
      setMessages((m) => [
        ...m,
        { id: `err-${Date.now()}`, role: 'ai', content: `Error: ${e.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  async function rate(messageId: string, rating: number) {
    await api.sendFeedback(messageId, rating)
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 40, background: 'var(--bg)', minHeight: '100vh' }}>
      <div className="chat-widget">
        <div className="chat-header">Chat with {orgSlug} Support</div>
        <div className="chat-body" ref={bodyRef}>
          {messages.length === 0 && (
            <div style={{ color: 'var(--text-dim)', fontSize: 13 }}>
              Ask a question — the AI will answer using this company's knowledge base.
            </div>
          )}
          {messages.map((m) => (
            <div key={m.id}>
              <div className={`bubble ${m.role}`}>{m.content}</div>
              {m.citations && m.citations.length > 0 && (
                <ul className="citation-list">
                  {m.citations.map((c, i) => (
                    <li key={i}>
                      📄 {c.document_title}: "{c.snippet.slice(0, 80)}..."
                    </li>
                  ))}
                </ul>
              )}
              {m.needs_human && (
                <div style={{ fontSize: 12, color: 'var(--warn)', marginTop: 4 }}>
                  ⚠️ A human agent has been notified and will follow up.
                </div>
              )}
              {m.role === 'ai' && !m.id.startsWith('err') && (
                <div className="feedback-row">
                  <button className="secondary" onClick={() => rate(m.id, 1)}>
                    👍
                  </button>
                  <button className="secondary" onClick={() => rate(m.id, -1)}>
                    👎
                  </button>
                </div>
              )}
            </div>
          ))}
          {loading && <div className="bubble ai">Thinking...</div>}
        </div>
        <div className="chat-input-row">
          <input
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
          />
          <button onClick={send}>Send</button>
        </div>
      </div>
    </div>
  )
}
