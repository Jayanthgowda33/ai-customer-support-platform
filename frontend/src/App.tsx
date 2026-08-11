import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './pages/Login'
import DashboardLayout from './pages/DashboardLayout'
import Overview from './pages/Overview'
import KnowledgeBase from './pages/KnowledgeBase'
import Conversations from './pages/Conversations'
import Tickets from './pages/Tickets'
import Analytics from './pages/Analytics'
import Widget from './pages/Widget'
import { getSession } from './lib/api'

export default function App() {
  const [authed, setAuthed] = useState(!!getSession().token)

  useEffect(() => {
    setAuthed(!!getSession().token)
  }, [])

  return (
    <Routes>
      <Route path="/widget/:orgSlug" element={<Widget />} />
      <Route path="/login" element={<Login onLoggedIn={() => setAuthed(true)} />} />
      <Route
        path="/"
        element={authed ? <DashboardLayout /> : <Navigate to="/login" replace />}
      >
        <Route index element={<Overview />} />
        <Route path="knowledge-base" element={<KnowledgeBase />} />
        <Route path="conversations" element={<Conversations />} />
        <Route path="tickets" element={<Tickets />} />
        <Route path="analytics" element={<Analytics />} />
      </Route>
    </Routes>
  )
}
