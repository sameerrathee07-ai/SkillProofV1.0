import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { Proposal } from '../types'
import { useAuth } from '../hooks/useAuth'

export default function MyProposalsPage() {
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [loading, setLoading] = useState(true)
  const { user: _user } = useAuth()

  useEffect(() => {
    api.get('/proposals/mine').then(r => { setProposals(r.data); setLoading(false) })
  }, [])

  if (loading) return <div className="container">Loading...</div>

  return (
    <div className="container">
      <h1 style={{ marginBottom: 24 }}>My Proposals</h1>
      {proposals.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 48 }}>
          <p>No proposals yet.</p>
          <Link to="/"><button style={{ marginTop: 16 }}>Browse Problems</button></Link>
        </div>
      ) : (
        <div className="proposal-list">
          {proposals.map(p => (
            <div key={p.id} className="proposal-item">
              <div className="proposal-header">
                <div>
                  <div className="proposal-title">Problem #{p.problem_id}</div>
                  <div className="proposal-meta">
                    <span>Status: <strong>{p.status}</strong></span>
                    <span>Gate Score: <strong>{p.gate_score.toFixed(1)}/10</strong></span>
                    <span>Attempts: {p.attempts}</span>
                  </div>
                </div>
                <div>
                  {p.status === 'submitted' && (
                    <button onClick={() => window.open(`/pdf/proposals/${p.id}`, '_blank')}>Download PDF</button>
                  )}
                </div>
              </div>
              <div className="score-grid">
                {p.dimension_scores.map((d: any) => (
                  <div key={d.name} className="score-card">
                    <div className="score">{d.score}/10</div>
                    <div className="label">{d.name}</div>
                  </div>
                ))}
              </div>
              {p.feedback && <div className="credibility"><strong>Feedback:</strong> {p.feedback}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}