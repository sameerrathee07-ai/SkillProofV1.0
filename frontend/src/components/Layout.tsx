import { useAuth } from '../hooks/useAuth'
import { Link, Outlet } from 'react-router-dom'

function NavBar() {
  const { user, logout } = useAuth()

  if (!user) return null

  return (
    <nav className="nav">
      <Link to="/" style={{ fontWeight: 700, fontSize: 18, color: '#1a1a2e' }}>SkillProof</Link>
      <div>
        <Link to="/" style={{ display: 'none' }}>Home</Link>
        {user.role === 'poster' && <>
          <Link to="/">Browse Problems</Link>
          <Link to="/post-problem">Post Problem</Link>
        </>}
        {user.role === 'solver' && <>
          <Link to="/">Browse Problems</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/my-proposals">My Proposals</Link>
        </>}
        <span style={{ marginLeft: 16, color: '#666' }}>{user.name} ({user.role})</span>
        <button onClick={logout} className="btn-secondary" style={{ marginLeft: 16, padding: '6px 12px', fontSize: 13 }}>Logout</button>
      </div>
    </nav>
  )
}

export default function Layout() {
  return (
    <>
      <NavBar />
      <Outlet />
    </>
  )
}