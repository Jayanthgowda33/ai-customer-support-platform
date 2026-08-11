import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { clearSession, getSession } from '../lib/api'

export default function DashboardLayout() {
  const navigate = useNavigate()
  const { role, org_slug } = getSession()

  function logout() {
    clearSession()
    navigate('/login')
  }

  const links = [
    { to: '/', label: 'Overview' },
    { to: '/conversations', label: 'Conversations' },
    { to: '/tickets', label: 'Tickets' },
    { to: '/knowledge-base', label: 'Knowledge Base' },
    { to: '/analytics', label: 'Analytics' },
  ]

  return (
    <div className="app-shell">
      <div className="sidebar">
        <h1>🤖 {org_slug}</h1>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === '/'}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            {l.label}
          </NavLink>
        ))}
        <div style={{ flex: 1 }} />
        <div style={{ fontSize: 12, color: 'var(--text-dim)', padding: '0 12px 8px' }}>
          Role: {role}
        </div>
        <button className="secondary" onClick={logout}>
          Log out
        </button>
      </div>
      <div className="main-content">
        <Outlet />
      </div>
    </div>
  )
}
