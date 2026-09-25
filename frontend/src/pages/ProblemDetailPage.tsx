import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import { Problem } from '../types'
import { useAuth } from '../hooks/useAuth'

export default function ProblemDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [problem, setProblem] = useState<Problem | null>(null)
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    api.get(`/problems/${id}`).then(r => { setProblem(r.data); setLoading(false) })
  }, [id])

  if (loading) return <div className="container">Loading...</div>
  if (!problem) return <div className="container">Problem not found</div>

  const handlePitch = () => {
    window.location.href = `/pitch/${id}`
  }

  return (
    <div className="container">
      <Link to="/" style={{ display: 'inline-block', marginBottom: 16, color: '#0066cc' }}>&larr; Back</Link>
      <div className="card">
        <h2 style={{ marginBottom: 16 }}>{problem.description}</h2>
        <div className="meta">
          <span className="tag">{problem.category}</span>
          <span className="tag">{problem.budget_range}</span>
          <span className="tag">{problem.timeline}</span>
        </div>
        {user?.role === 'solver' && (
          <button onClick={handlePitch} style={{ marginTop: 16, width: '100%' }}>
            Start Pitch (10 tokens for full pitch)
          </button>
        )}
        {user?.role === 'poster' && (
          <Link to={`/proposals/${problem.id}`}>
            <button className="btn-secondary" style={{ marginTop: 16, width: '100%' }}>
              View Proposals
            </button>
          </Link>
        )}
      </div>
    </div>
  )
}