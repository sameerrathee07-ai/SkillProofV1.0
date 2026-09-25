import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../services/api'
import { ScoreResponse, DimensionScore } from '../types'
import { useAuth } from '../hooks/useAuth'

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<ScoreResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const { user: _user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    api.get(`/pitch/${id}`).then(r => {
      const session = r.data
      if (session.completed && session.pitch_text) {
        api.post(`/pitch/${id}/score`).then(res => setData(res.data)).finally(() => setLoading(false))
      } else {
        setLoading(false)
      }
    })
  }, [id])

  if (loading) return <div className="container">Loading...</div>
  if (!data) return <div className="container"><Link to={`/pitch/${id}`}><button>Complete pitch first</button></Link></div>

  const getScoreClass = (score: number) =>
    score >= 7 ? 'pass' : score >= 5 ? 'warn' : 'fail'

  return (
    <div className="container">
      <h1 style={{ marginBottom: 8 }}>{data.passed ? '✅ Pitch Passed!' : '❌ Pitch Needs Work'}</h1>
      <p style={{ marginBottom: 24, color: '#666' }}>
        Gate score: <strong>{data.gate_score.toFixed(1)}/10</strong> (need 6.0+)
      </p>

      <div className="score-grid">
        {data.dimension_scores.map((d: DimensionScore) => (
          <div key={d.name} className={`score-card ${getScoreClass(d.score)}`}>
            <div className="score">{d.score}/10</div>
            <div className="label">{d.name}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Feedback</h3>
        <p>{data.feedback}</p>
      </div>

      {data.passed ? (
        <>
          <div className="success" style={{ marginTop: 16 }}>Proposal submitted! Problem poster can now view it.</div>
          <button onClick={() => navigate('/my-proposals')} style={{ marginTop: 16 }}>View My Proposals</button>
        </>
      ) : (
        <>
          <button onClick={() => navigate(`/pitch/${id}`)} style={{ marginTop: 16 }}>Revise & Resubmit</button>
        </>
      )}
    </div>
  )
}