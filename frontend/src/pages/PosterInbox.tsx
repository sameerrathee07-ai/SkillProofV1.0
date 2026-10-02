import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { pitchApi, pdfApi } from '../utils/api';
import type { Proposal } from '../types';

export default function PosterInbox() {
  const { user } = useAuth();
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProblemId, setSelectedProblemId] = useState<number | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState<number | null>(null);

  useEffect(() => {
    const fetchProposals = async () => {
      try {
        const problemsRes = await pitchApi.problemProposals(0);
      } catch (err) {
        console.error('Failed to load proposals:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProposals();
  }, []);

  const fetchProposalsForProblem = async (problemId: number) => {
    try {
      const res = await pitchApi.problemProposals(problemId);
      setProposals(res.data);
      setSelectedProblemId(problemId);
    } catch (err) {
      console.error('Failed to load proposals:', err);
    }
  };

  const handleDownloadPdf = async (proposalId: number) => {
    setDownloadingPdf(proposalId);
    try {
      const blob = await pdfApi.download(proposalId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `proposal_${proposalId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to download PDF');
    } finally {
      setDownloadingPdf(null);
    }
  };

  if (loading) {
    return <div className="text-center text-secondary py-8">Loading...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Inbox</h1>
        <p className="page-subtitle">Vetted proposals for your problems, ranked by gate score and solver credibility</p>
      </div>

      <div className="card mb-6" style={{ padding: '1.5rem' }}>
        <h3 className="font-semibold mb-3">Select a Problem</h3>
        <p className="text-secondary text-sm mb-3">Choose a problem to view its proposals.</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {proposals.map(p => (
            <button
              key={p.problem_id}
              onClick={() => fetchProposalsForProblem(p.problem_id)}
              className={`btn ${selectedProblemId === p.problem_id ? 'btn-primary' : 'btn-secondary'} text-sm`}
            >
              Problem #{p.problem_id} ({p.problem_title?.slice(0, 40)}...)
            </button>
          ))}
        </div>
      </div>

      {selectedProblemId && proposals.length > 0 && (
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 className="font-semibold mb-4">Proposals for Problem #{selectedProblemId}</h3>
          {proposals.filter(p => p.problem_id === selectedProblemId).length === 0 ? (
            <p className="text-secondary">No submitted proposals yet.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {proposals.filter(p => p.problem_id === selectedProblemId).map((proposal, index) => (
                <div key={proposal.id} style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', padding: '1rem', background: 'var(--color-bg)', borderBottom: '1px solid var(--color-border)' }}>
                    <div>
                      <div className="font-semibold">#{index + 1} • {proposal.solver_name}</div>
                      <div className="text-sm text-secondary mt-1">
                        <span className="badge badge-success">Score: {proposal.gate_score}/100</span>
                        {proposal.solver_credibility && (
                          <>
                            <span className="ml-2 badge badge-info">Avg: {proposal.solver_credibility.avg_gate_score}</span>
                            <span className="ml-2 badge badge-secondary">Passes: {proposal.solver_credibility.total_passes}/{proposal.solver_credibility.total_attempts}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => handleDownloadPdf(proposal.id)}
                      disabled={downloadingPdf === proposal.id}
                      className="btn btn-primary"
                    >
                      {downloadingPdf === proposal.id ? 'Downloading...' : 'Download PDF'}
                    </button>
                  </div>
                  <div style={{ padding: '1rem' }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {proposal.dimension_scores && JSON.parse(proposal.dimension_scores).map((dim: any, i: number) => (
                        <span key={i} className="badge badge-secondary text-xs">
                          {dim.dimension}: {dim.score}/10
                        </span>
                      ))}
                    </div>
                    {proposal.feedback && (
                      <p className="text-sm text-secondary mt-2"><strong>Feedback:</strong> {proposal.feedback}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}