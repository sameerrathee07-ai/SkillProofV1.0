import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { pitchApi, pdfApi } from '../utils/api';
import type { Proposal, DimensionScore } from '../types';

export default function PitchResults() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [loading, setLoading] = useState(true);
  const [scoring, setScoring] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  useEffect(() => {
    const fetchProposal = async () => {
      try {
        const proposalsRes = await pitchApi.myProposals();
        const userProposals = proposalsRes.data.filter(p => p.pitch_session_id === parseInt(sessionId!));
        if (userProposals.length > 0) {
          setProposal(userProposals[0]);
        } else {
          setScoring(true);
        }
      } catch (err) {
        console.error('Failed to load proposal:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProposal();
  }, [sessionId]);

  const handleScore = async () => {
    setScoring(true);
    try {
      const res = await pitchApi.score(parseInt(sessionId!));
      const proposalsRes = await pitchApi.myProposals();
      const userProposals = proposalsRes.data.filter(p => p.pitch_session_id === parseInt(sessionId!));
      if (userProposals.length > 0) {
        setProposal(userProposals[0]);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to score pitch');
    } finally {
      setScoring(false);
    }
  };

  const handleRevise = async () => {
    if (!proposal) return;
    try {
      const res = await pitchApi.revise(proposal.id);
      navigate(`/pitch/${res.data.session_id}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start revision');
    }
  };

  const handleDownloadPdf = async () => {
    if (!proposal) return;
    setDownloadingPdf(true);
    try {
      const blob = await pdfApi.download(proposal.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `proposal_${proposal.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to download PDF');
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loading) {
    return <div className="text-center text-secondary py-8">Loading...</div>;
  }

  if (scoring) {
    return (
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        <div className="card" style={{ padding: '3rem', textAlign: 'center' }}>
          <div className="badge badge-info mb-4" style={{ fontSize: '1rem', padding: '0.75rem 1.5rem' }}>
            Scoring your pitch...
          </div>
          <button onClick={handleScore} className="btn btn-primary" disabled={scoring}>
            {scoring ? 'Scoring...' : 'Score Pitch'}
          </button>
        </div>
      </div>
    );
  }

  if (!proposal) {
    return (
      <div className="card" style={{ padding: '3rem', textAlign: 'center' }}>
        <h2 className="text-xl font-semibold mb-2">No proposal found</h2>
        <p className="text-secondary mb-4">Complete a pitch session first.</p>
      </div>
    );
  }

  const dimensionScores: DimensionScore[] = proposal.dimension_scores ? JSON.parse(proposal.dimension_scores) : [];
  const gatePassed = proposal.status === 'submitted';
  const gateScore = proposal.gate_score || 0;

  return (
    <div style={{ maxWidth: '900px' }}>
      <div className="page-header">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="page-title">Pitch Results</h1>
            <p className="page-subtitle">Session {sessionId} • Attempt {proposal.attempts}</p>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${gatePassed ? 'text-success' : 'text-error'}`}>
              {gateScore}/100
            </div>
            <span className={`badge ${gatePassed ? 'badge-success' : 'badge-warning'}`}>
              {gatePassed ? 'Passed Gate' : 'Needs Work'}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-2 mb-6">
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 className="font-semibold mb-4">Dimension Scores</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {dimensionScores.map((dim, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ width: '200px', fontSize: '0.875rem', fontWeight: 500 }}>{dim.dimension}</div>
                <div style={{ flex: 1, height: '8px', background: 'var(--color-border)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${dim.score * 10}%`,
                      background: dim.score >= 7 ? 'var(--color-success)' : dim.score >= 5 ? 'var(--color-accent)' : 'var(--color-error)',
                      transition: 'width 0.3s ease',
                    }}
                  />
                </div>
                <div className="font-semibold" style={{ width: '40px', textAlign: 'right' }}>{dim.score}/10</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 className="font-semibold mb-4">Feedback</h3>
          <div className="p-4" style={{ background: 'var(--color-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
            <p className="text-secondary">{proposal.feedback || 'No specific feedback available.'}</p>
          </div>

          {proposal.status === 'needs_work' && (
            <div className="mt-4">
              <button onClick={handleRevise} className="btn btn-primary w-full">
                Revise and Resubmit
              </button>
              <p className="text-xs text-secondary text-center mt-2">
                Only edited steps will be re-validated and charged.
              </p>
            </div>
          )}

          {proposal.status === 'submitted' && (
            <div className="mt-4">
              <button onClick={handleDownloadPdf} className="btn btn-secondary w-full" disabled={downloadingPdf}>
                {downloadingPdf ? 'Generating PDF...' : 'Download Proposal PDF'}
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="card" style={{ padding: '1.5rem' }}>
        <h3 className="font-semibold mb-4">Proposal Outline</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {[
            { key: 'Problem', label: 'Problem' },
            { key: 'Solution', label: 'Solution' },
            { key: 'Affected People', label: 'Affected People' },
            { key: 'Cost and Value', label: 'Cost and Value' },
            { key: 'Alternatives and Edge', label: 'Alternatives and Edge' },
            { key: 'Solver and Advantage', label: 'Solver and Advantage' },
            { key: 'Proposed Next Step', label: 'Proposed Next Step' },
          ].map(({ key, label }) => (
            <div key={key} style={{ padding: '1rem', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
              <div className="font-medium text-sm text-secondary mb-1">{label}</div>
              <div className="text-sm">{proposal.dimension_scores ? '' : 'Outline not available until scored.'}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}