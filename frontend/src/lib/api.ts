const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function getToken(): string | null {
  return localStorage.getItem('token')
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth = true
): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { ...headers, ...(options.headers as Record<string, string> | undefined) },
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || 'Request failed')
  }
  if (res.status === 204) return undefined as unknown as T
  return res.json()
}

export const api = {
  login: (email: string, password: string, org_slug: string) =>
    request<{ access_token: string; role: string; organization: string }>(
      '/auth/login',
      { method: 'POST', body: JSON.stringify({ email, password, org_slug }) },
      false
    ),

  registerOrg: (payload: {
    org_name: string
    org_slug: string
    admin_email: string
    admin_full_name: string
    admin_password: string
  }) =>
    request<{ access_token: string }>(
      '/auth/register-organization',
      { method: 'POST', body: JSON.stringify(payload) },
      false
    ),

  me: () => request<{ id: string; email: string; full_name: string; role: string }>('/auth/me'),

  listDocuments: () => request<any[]>('/documents'),
  uploadTextDocument: (title: string, content: string) =>
    request('/documents/text', { method: 'POST', body: JSON.stringify({ title, content }) }),
  deleteDocument: (id: string) => request(`/documents/${id}`, { method: 'DELETE' }),

  listConversations: () => request<any[]>('/conversations'),
  getMessages: (conversationId: string) =>
    request<any[]>(`/conversations/${conversationId}/messages`),
  agentReply: (conversationId: string, content: string) =>
    request(`/conversations/${conversationId}/reply?content=${encodeURIComponent(content)}`, {
      method: 'POST',
    }),

  listTickets: (status?: string) =>
    request<any[]>(`/tickets${status ? `?status=${status}` : ''}`),
  updateTicket: (id: string, payload: any) =>
    request(`/tickets/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),

  getAnalytics: () => request<any>('/analytics'),

  // Public, unauthenticated — used by the customer-facing chat widget
  sendChatMessage: (payload: {
    org_slug: string
    customer_identifier: string
    message: string
    conversation_id?: string
  }) =>
    request<any>('/chat', { method: 'POST', body: JSON.stringify(payload) }, false),

  sendFeedback: (message_id: string, rating: number) =>
    request('/feedback', { method: 'POST', body: JSON.stringify({ message_id, rating }) }, false),
}

export function saveSession(token: string, role: string, organization: string) {
  localStorage.setItem('token', token)
  localStorage.setItem('role', role)
  localStorage.setItem('org_slug', organization)
}

export function clearSession() {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('org_slug')
}

export function getSession() {
  return {
    token: localStorage.getItem('token'),
    role: localStorage.getItem('role'),
    org_slug: localStorage.getItem('org_slug'),
  }
}
