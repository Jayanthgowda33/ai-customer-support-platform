import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, saveSession } from '../lib/api'

export default function Login({ onLoggedIn }: { onLoggedIn: () => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [orgSlug, setOrgSlug] = useState('acme')
  const [email, setEmail] = useState('admin@acme.com')
  const [password, setPassword] = useState('password123')
  const [orgName, setOrgName] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      const res = await api.login(email, password, orgSlug)
      saveSession(res.access_token, res.role, res.organization)
      onLoggedIn()
      navigate('/')
    } catch (err: any) {
      setError(err.message)
    }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      const res = await api.registerOrg({
        org_name: orgName,
        org_slug: orgSlug,
        admin_email: email,
        admin_full_name: fullName,
        admin_password: password,
      })
      saveSession(res.access_token, 'owner', orgSlug)
      onLoggedIn()
      navigate('/')
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <div className="login-screen">
      <form className="card login-box" onSubmit={mode === 'login' ? handleLogin : handleRegister}>
        <h2 style={{ margin: 0 }}>AI Support Platform</h2>
        <p style={{ color: 'var(--text-dim)', marginTop: -8 }}>
          {mode === 'login' ? 'Sign in to your organization' : 'Create a new organization'}
        </p>

        {mode === 'register' && (
          <>
            <label>Organization name</label>
            <input value={orgName} onChange={(e) => setOrgName(e.target.value)} required />
            <label>Your full name</label>
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          </>
        )}

        <label>Organization slug</label>
        <input value={orgSlug} onChange={(e) => setOrgSlug(e.target.value)} required />

        <label>Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <div style={{ color: 'var(--danger)', fontSize: 13 }}>{error}</div>}

        <button type="submit">{mode === 'login' ? 'Sign in' : 'Create organization'}</button>

        <div style={{ fontSize: 13, textAlign: 'center', color: 'var(--text-dim)' }}>
          {mode === 'login' ? (
            <>
              New here?{' '}
              <a onClick={() => setMode('register')} style={{ cursor: 'pointer' }}>
                Register an organization
              </a>
            </>
          ) : (
            <>
              Already have an account?{' '}
              <a onClick={() => setMode('login')} style={{ cursor: 'pointer' }}>
                Sign in
              </a>
            </>
          )}
        </div>

        <div style={{ fontSize: 12, color: 'var(--text-dim)', marginTop: 8 }}>
          Demo login is pre-filled: org <code>acme</code>, admin@acme.com / password123
        </div>
      </form>
    </div>
  )
}
