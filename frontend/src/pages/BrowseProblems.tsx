import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { problemsApi } from '../utils/api';
import type { Problem } from '../types';

export default function BrowseProblems() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProblems = async () => {
      try {
        const res = await problemsApi.list();
        setProblems(res.data);
      } catch (err) {
        console.error('Failed to load problems:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProblems();
  }, []);

  if (loading) {
    return <div className="text-center text-secondary py-8">Loading problems...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Browse Problems</h1>
        <p className="page-subtitle">Find real operational problems to solve. Each problem shows budget, timeline, and category.</p>
      </div>

      {problems.length === 0 ? (
        <div className="card" style={{ padding: '3rem', textAlign: 'center' }}>
          <p className="text-secondary mb-4">No open problems at the moment.</p>
          <p className="text-sm text-secondary">Check back later or post your own problem if you're a problem poster.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {problems.map(problem => (
            <Link key={problem.id} to={`/problems/${problem.id}`} className="card" style={{ padding: '1.5rem', textDecoration: 'none', color: 'inherit', transition: 'box-shadow var(--transition)', display: 'block' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="badge badge-info">{problem.category}</span>
                    <span className="badge badge-secondary">{problem.status}</span>
                  </div>
                  <h3 className="text-lg font-semibold mb-1">{problem.description.slice(0, 120)}...</h3>
                  <p className="text-sm text-secondary mb-2">Posted by {problem.poster_name}</p>
                  <div className="flex flex-wrap gap-3 text-sm text-secondary">
                    <span><strong>Budget:</strong> {problem.budget_range}</span>
                    <span><strong>Timeline:</strong> {problem.timeline}</span>
                  </div>
                </div>
                <span className="btn btn-primary" style={{ whiteSpace: 'nowrap' }}>View Details</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}