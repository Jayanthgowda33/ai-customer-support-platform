import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function KnowledgeBase() {
  const [docs, setDocs] = useState<any[]>([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [error, setError] = useState('')

  function refresh() {
    api.listDocuments().then(setDocs).catch((e) => setError(e.message))
  }

  useEffect(() => {
    refresh()
  }, [])

  async function addDoc(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await api.uploadTextDocument(title, content)
      setTitle('')
      setContent('')
      refresh()
    } catch (err: any) {
      setError(err.message)
    }
  }

  async function removeDoc(id: string) {
    await api.deleteDocument(id)
    refresh()
  }

  return (
    <div>
      <h2>Knowledge Base</h2>
      <p style={{ color: 'var(--text-dim)' }}>
        Add FAQs, product docs, or paste any reference text. Content is automatically chunked
        and embedded for RAG retrieval.
      </p>

      <form className="card" onSubmit={addDoc} style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
        <label>Title</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
        <label>Content</label>
        <textarea rows={6} value={content} onChange={(e) => setContent(e.target.value)} required />
        {error && <div style={{ color: 'var(--danger)', fontSize: 13 }}>{error}</div>}
        <button type="submit" style={{ width: 160 }}>
          Add document
        </button>
      </form>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Type</th>
              <th>Added</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.id}>
                <td>{d.title}</td>
                <td>{d.source_type}</td>
                <td>{new Date(d.created_at).toLocaleString()}</td>
                <td>
                  <button className="danger" onClick={() => removeDoc(d.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {docs.length === 0 && (
              <tr>
                <td colSpan={4} style={{ color: 'var(--text-dim)' }}>
                  No documents yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
