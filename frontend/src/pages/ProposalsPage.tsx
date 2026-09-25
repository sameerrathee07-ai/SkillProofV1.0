import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import { Proposal } from '../types'
import { useAuth } from '../hooks/useAuth'

export default function ProposalsPage() {
  const { id } = useParams<{ id: string }>()
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [loading, setLoading] = useState(true)
  const { user: _user } = useAuth()

  useEffect(() => {
    api.get(`/proposals/problems/${id}`).then(r => { setProposals(r.data); setLoading(false) })
  }, [id])

  if (loading) return <div className="container">Loading...</div>

  return (
    <div className="container">
      <Link to="/" style={{ display: 'inline-block', marginBottom: 16, color: '#0066cc' }}>&larr; Back</Link>
      <h1 style={{ marginBottom: 24 }}>Proposals for Problem #{id}</h1>
      {proposals.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 48 }}>
          <p>No proposals yet.</p>
        </div>
      ) : (
        <div className="proposal-list">
          {proposals.map(p => (
            <div key={p.id} className="proposal-item">
              <div className="proposal-header">
                <div>
                  <div className="proposal-title">Solver: {p.solver_name}</div>
                  <div className="proposal-meta">
                    <span>Gate Score: <strong>{p.gate_score.toFixed(1)}/10</strong></span>
                    <span>Attempts: {p.attempts}</span>
                  </div>
                </div>
                <div>
                  <button onClick={() => window.open(`/pdf/proposals/${p.id}`, '_blank')}>Download PDF</button>
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
              {p.solver_credibility && (
                <div className="credibility">
                  <strong>Solver Credibility</strong>
                  <div className="credibility-row"><span>Avg Gate Score</span><span>{p.solver_credibility.avg_gate_score}/10</span></div>
                  <div className="credibility-row"><span>First-Attempt Passes</span><span>{p.solver_credibility.first_attempt_passes}</span></div>
                  <div className="credibility-row"><span>Total Passes</span><span>{p.solver_credibility.total_passes}</span></div>
                  <div className="credibility-row"><span>Total Attempts</span><span>{p.solver_credibility.total_attempts}</span></div>
                </div>
              )}
              {p.feedback && <div className="credibility" style={{ marginTop: 12 }}><strong>Feedback:</strong> {p.feedback}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}