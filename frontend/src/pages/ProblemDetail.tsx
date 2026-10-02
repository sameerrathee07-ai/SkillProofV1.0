import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { problemsApi, pitchApi } from '../utils/api';
import type { Problem } from '../types';

export default function ProblemDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);
  const [startingPitch, setStartingPitch] = useState(false);

  useEffect(() => {
    const fetchProblem = async () => {
      try {
        const res = await problemsApi.get(parseInt(id!));
        setProblem(res.data);
      } catch (err) {
        console.error('Failed to load problem:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProblem();
  }, [id]);

  const handleStartPitch = async () => {
    if (!user) return;
    setStartingPitch(true);
    try {
      const res = await pitchApi.start(parseInt(id!));
      window.location.href = `/pitch/${res.data.session_id}`;
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start pitch');
    } finally {
      setStartingPitch(false);
    }
  };

  if (loading) {
    return <div className="text-center text-secondary py-8">Loading...</div>;
  }

  if (!problem) {
    return (
      <div className="card" style={{ padding: '3rem', textAlign: 'center' }}>
        <h2 className="text-xl font-semibold mb-2">Problem not found</h2>
        <Link to="/problems" className="btn btn-primary">Browse Problems</Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px' }}>
      <div className="page-header">
        <div className="flex items-center gap-2 mb-2">
          <span className="badge badge-info">{problem.category}</span>
          <span className={`badge ${problem.status === 'open' ? 'badge-success' : 'badge-warning'}`}>{problem.status}</span>
        </div>
        <h1 className="page-title">{problem.description}</h1>
        <p className="page-subtitle">Posted by {problem.poster_name} • {new Date(problem.created_at).toLocaleDateString()}</p>
      </div>

      <div className="card mb-6" style={{ padding: '1.5rem' }}>
        <div className="grid grid-2">
          <div>
            <h3 className="font-semibold mb-2">Budget / Value Range</h3>
            <p className="text-secondary">{problem.budget_range}</p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Timeline</h3>
            <p className="text-secondary">{problem.timeline}</p>
          </div>
        </div>
      </div>

      {user?.role === 'solver' && problem.status === 'open' && (
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 className="font-semibold mb-2">Start a Pitch</h3>
          <p className="text-secondary mb-4">
            The pitch gate has 5 steps. Each accepted answer costs 2 tokens. 
            Pass mark: 6/10 average across 6 dimensions. 
            You'll see the exact criteria before starting.
          </p>
          <button
            onClick={handleStartPitch}
            disabled={startingPitch}
            className="btn btn-primary"
          >
            {startingPitch ? 'Starting...' : 'Start Pitch (Costs 2 tokens per answer)'}
          </button>
        </div>
      )}

      {user?.role === 'poster' && user.id === problem.poster_id && (
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 className="font-semibold mb-2">Problem Owner Actions</h3>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link to="/inbox" className="btn btn-primary">View Proposals</Link>
            {problem.status === 'open' && (
              <button className="btn btn-error" onClick={async () => {
                try {
                  await problemsApi.close(problem.id);
                  window.location.reload();
                } catch (err) {
                  alert('Failed to close problem');
                }
              }}>
                Close Problem
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}