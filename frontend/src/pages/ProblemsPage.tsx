import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { Problem } from '../types'
import { useAuth } from '../hooks/useAuth'

export default function ProblemsPage() {
  const [problems, setProblems] = useState<Problem[]>([])
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    api.get('/problems').then(r => { setProblems(r.data); setLoading(false) })
  }, [])

  if (loading) return <div className="container">Loading...</div>

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Open Problems</h1>
        {user?.role === 'poster' && (
          <Link to="/post-problem"><button>Post Problem</button></Link>
        )}
      </div>
      {problems.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 48 }}>
          <p>No open problems yet.</p>
          {user?.role === 'poster' && <Link to="/post-problem"><button style={{ marginTop: 16 }}>Post the first one</button></Link>}
        </div>
      ) : (
        <div>
          {problems.map(p => (
            <Link key={p.id} to={`/problems/${p.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
              <div className="problem-card">
                <h3>{p.description.substring(0, 100)}...</h3>
                <div className="meta">
                  <span>{p.category}</span>
                  <span>{p.budget_range}</span>
                  <span>{p.timeline}</span>
                </div>
                <div className="tags">
                  <span className="tag">View & Pitch</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}