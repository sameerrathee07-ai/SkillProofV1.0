import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { problemsApi, pitchApi, tokensApi } from '../utils/api';
import type { Problem, Proposal, TokenBalance } from '../types';

export default function Dashboard() {
  const { user } = useAuth();
  const [problems, setProblems] = useState<Problem[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [balance, setBalance] = useState<TokenBalance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [problemsRes, proposalsRes, balanceRes] = await Promise.all([
          problemsApi.list(),
          user?.role === 'solver' ? pitchApi.myProposals() : Promise.resolve({ data: [] }),
          user?.role === 'solver' ? tokensApi.balance() : Promise.resolve({ data: { balance: 0 } }),
        ]);
        setProblems(problemsRes.data);
        setProposals(proposalsRes.data);
        setBalance(balanceRes.data);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  if (loading) {
    return <div className="text-center text-secondary py-8">Loading...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Welcome back, {user?.name}</p>
      </div>

      {user?.role === 'solver' && balance && (
        <div className="card mb-6" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div className="text-sm text-secondary">Token Balance</div>
            <div className="text-3xl font-bold text-primary">{balance.balance}</div>
          </div>
          <Link to="/tokens" className="btn btn-primary">Buy Tokens</Link>
        </div>
      )}

      <div className="grid grid-2 mb-8">
        <div className="card" style={{ padding: '1.5rem' }}>
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-lg font-semibold">{user?.role === 'poster' ? 'My Problems' : 'Open Problems'}</h2>
            <Link to={user?.role === 'poster' ? '/problems/post' : '/problems'} className="btn btn-secondary text-sm">View All</Link>
          </div>
          {problems.slice(0, 3).length === 0 ? (
            <p className="text-secondary text-sm">No problems yet.</p>
          ) : (
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {problems.slice(0, 3).map(p => (
                <li key={p.id} style={{ padding: '0.75rem', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
                  <Link to={`/problems/${p.id}`} className="font-medium hover:text-primary">{p.description.slice(0, 80)}...</Link>
                  <div className="text-xs text-secondary mt-1">{p.category} • {p.budget_range} • {p.timeline}</div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {user?.role === 'solver' && (
          <div className="card" style={{ padding: '1.5rem' }}>
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-lg font-semibold">My Proposals</h2>
              <Link to="/problems" className="btn btn-secondary text-sm">Browse More</Link>
            </div>
            {proposals.slice(0, 3).length === 0 ? (
              <p className="text-secondary text-sm">No proposals yet. <Link to="/problems" className="text-primary">Browse problems</Link> to get started.</p>
            ) : (
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {proposals.slice(0, 3).map(p => (
                  <li key={p.id} style={{ padding: '0.75rem', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
                    <div className="font-medium">{p.problem_title || 'Problem'}</div>
                    <div className="text-xs text-secondary mt-1">
                      <span className={`badge ${p.status === 'submitted' ? 'badge-success' : 'badge-warning'}`}>{p.status}</span>
                      {p.gate_score && <span className="ml-2">Score: {p.gate_score}/100</span>}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {user?.role === 'poster' && (
          <div className="card" style={{ padding: '1.5rem' }}>
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-lg font-semibold">Proposals Received</h2>
              <Link to="/inbox" className="btn btn-secondary text-sm">View Inbox</Link>
            </div>
            <p className="text-secondary text-sm">Check your inbox for vetted proposals on your problems.</p>
          </div>
        )}
      </div>

      <div className="card" style={{ padding: '1.5rem' }}>
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          {user?.role === 'poster' && (
            <Link to="/problems/post" className="btn btn-primary">Post a Problem</Link>
          )}
          {user?.role === 'solver' && (
            <>
              <Link to="/problems" className="btn btn-primary">Browse Problems</Link>
              <Link to="/tokens" className="btn btn-secondary">Manage Tokens</Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}