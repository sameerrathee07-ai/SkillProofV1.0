import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import { FileText, RotateCcw, ArrowRight } from 'lucide-react';

export const SolverDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [proposals, setProposals] = useState<any[]>([]);
  const [tab, setTab] = useState<'all' | 'submitted' | 'needs_work'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchMyProposals();
  }, [tab]);

  const fetchMyProposals = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiFetch(`/my-proposals?status=${tab}`);
      setProposals(data.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load proposals.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 border-b border-ink/10 pb-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-widest text-brass">Solver Workspace</span>
          <h1 className="text-3xl sm:text-4xl font-serif font-bold text-ink mt-1">My Proposals & Pitches</h1>
        </div>

        {/* Tab Filters */}
        <div className="flex items-center gap-2">
          {[
            { key: 'all', label: 'All Submissions' },
            { key: 'submitted', label: 'Passed Gate' },
            { key: 'needs_work', label: 'Needs Work' },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key as any)}
              className={`px-4 py-2 rounded-full text-xs font-bold transition-all ${
                tab === t.key
                  ? 'bg-brass text-ink shadow-sm'
                  : 'bg-ivory border border-ink/20 text-ink-muted hover:border-ink/40'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brass mx-auto"></div>
        </div>
      ) : error ? (
        <div className="p-4 bg-brick-light text-brick rounded-lg text-xs font-semibold border border-brick/30 text-center">
          {error}
        </div>
      ) : proposals.length === 0 ? (
        <div className="text-center py-16 bg-ivory border border-dashed border-ink/20 rounded-2xl p-8 space-y-3">
          <FileText className="w-10 h-10 text-ink-muted mx-auto" />
          <h3 className="text-lg font-serif font-bold text-ink">No proposals found</h3>
          <p className="text-xs text-ink-muted">Browse open problems and launch a 5-step pitch session to clear the gate.</p>
          <button
            onClick={() => navigate('/problems')}
            className="mt-4 px-6 py-2.5 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors text-xs"
          >
            Browse Open Problems
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {proposals.map((item) => (
            <div
              key={item.proposal_id}
              className="bg-ivory border border-ink/10 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
            >
              <div className="space-y-2 max-w-2xl">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full bg-forest-light text-forest text-[10px] font-bold">
                    {item.category}
                  </span>
                  <span className="text-xs text-ink-muted">
                    Submitted: {item.submitted_at ? new Date(item.submitted_at).toLocaleDateString() : 'Recent'}
                  </span>
                </div>
                <h3 className="font-serif font-bold text-xl text-ink leading-snug">
                  {item.problem_title}
                </h3>
                {item.weakest_dimension && item.status === 'needs_work' && (
                  <p className="text-xs text-brick font-medium">
                    ⚠ Weakest Dimension: <span className="capitalize">{item.weakest_dimension.replace('_', ' ')}</span>
                  </p>
                )}
              </div>

              <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end">
                <div className="text-right">
                  <div className="text-xs text-ink-muted font-medium">Gate Score</div>
                  <div className="text-xl font-serif font-bold text-ink">{item.score} / 10</div>
                </div>

                {item.status === 'submitted' ? (
                  <button
                    onClick={() => navigate(`/proposals/${item.proposal_id}`)}
                    className="px-5 py-2.5 bg-forest text-ivory font-semibold rounded-lg hover:bg-forest-hover transition-colors shadow-sm text-xs flex items-center gap-1.5"
                  >
                    <span>View Proposal</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <button
                    onClick={() => navigate(`/pitch/${item.problem_id}`)}
                    className="px-5 py-2.5 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors shadow-sm text-xs flex items-center gap-1.5"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Revise & Resubmit</span>
                  </button>
                )}
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
};
