import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import { Building2, PlusCircle, ArrowRight, Eye } from 'lucide-react';

export const PosterDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'published' | 'closed'>('published');

  // Selected problem proposals modal/expand
  const [selectedProblemProposals, setSelectedProblemProposals] = useState<any[] | null>(null);
  const [selectedProblemTitle, setSelectedProblemTitle] = useState('');

  useEffect(() => {
    fetchListings();
  }, [activeTab]);

  const fetchListings = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiFetch(`/my-listings?status=${activeTab}`);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load listings.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewProposals = async (problemId: string, title: string) => {
    try {
      const res = await apiFetch(`/problems/${problemId}/proposals`);
      setSelectedProblemProposals(res.items || []);
      setSelectedProblemTitle(title);
    } catch (err: any) {
      alert(err.message || 'Failed to fetch proposals.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Header & Metrics Panel */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-ink/10 pb-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-widest text-brass">Problem Poster Workspace</span>
          <h1 className="text-3xl sm:text-4xl font-serif font-bold text-ink mt-1">My Posted Listings</h1>
        </div>

        <button
          onClick={() => navigate('/post-problem')}
          className="px-6 py-3 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors shadow-sm flex items-center gap-2 text-sm"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Post New Problem</span>
        </button>
      </div>

      {/* Top Metrics Panel */}
      {data?.metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="bg-ivory border border-ink/10 p-6 rounded-2xl shadow-sm space-y-2">
            <span className="text-xs text-ink-muted font-medium uppercase tracking-wider">Total Posted Problems</span>
            <div className="text-3xl font-serif font-bold text-ink">{data.metrics.total_posted}</div>
          </div>

          <div className="bg-ivory border border-ink/10 p-6 rounded-2xl shadow-sm space-y-2">
            <span className="text-xs text-ink-muted font-medium uppercase tracking-wider">Avg Proposals / Problem</span>
            <div className="text-3xl font-serif font-bold text-brass">{data.metrics.avg_proposals_per_problem}</div>
          </div>

          <div className="bg-ivory border border-ink/10 p-6 rounded-2xl shadow-sm space-y-2">
            <span className="text-xs text-ink-muted font-medium uppercase tracking-wider">Problems Solved</span>
            <div className="text-3xl font-serif font-bold text-forest">{data.metrics.total_solved}</div>
          </div>
        </div>
      )}

      {/* Active vs Closed Tabs */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setActiveTab('published')}
          className={`px-4 py-2 rounded-full text-xs font-bold transition-all ${
            activeTab === 'published'
              ? 'bg-brass text-ink shadow-sm'
              : 'bg-ivory border border-ink/20 text-ink-muted hover:border-ink/40'
          }`}
        >
          Active Listings
        </button>
        <button
          onClick={() => setActiveTab('closed')}
          className={`px-4 py-2 rounded-full text-xs font-bold transition-all ${
            activeTab === 'closed'
              ? 'bg-brass text-ink shadow-sm'
              : 'bg-ivory border border-ink/20 text-ink-muted hover:border-ink/40'
          }`}
        >
          Closed / Solved
        </button>
      </div>

      {loading ? (
        <div className="text-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brass mx-auto"></div>
        </div>
      ) : error ? (
        <div className="p-4 bg-brick-light text-brick rounded-lg text-xs font-semibold border border-brick/30 text-center">
          {error}
        </div>
      ) : data?.items?.length === 0 ? (
        <div className="text-center py-16 bg-ivory border border-dashed border-ink/20 rounded-2xl p-8 space-y-3">
          <Building2 className="w-10 h-10 text-ink-muted mx-auto" />
          <h3 className="text-lg font-serif font-bold text-ink">No listings found</h3>
          <p className="text-xs text-ink-muted">Post your first operational problem to receive pre-vetted proposals.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {data?.items?.map((item: any) => (
            <div
              key={item.problem_id}
              className="bg-ivory border border-ink/10 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
            >
              <div className="space-y-2 max-w-2xl">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full bg-forest-light text-forest text-[10px] font-bold">
                    {item.category}
                  </span>
                  <span className="text-xs text-ink-muted">
                    {item.budget_range} • {item.timeline}
                  </span>
                </div>

                <h3 className="font-serif font-bold text-xl text-ink leading-snug">
                  {item.title}
                </h3>
              </div>

              <div className="flex items-center gap-6 w-full md:w-auto justify-between md:justify-end">
                <div className="text-right">
                  <div className="text-xs text-ink-muted font-medium">Proposals Received</div>
                  <div className="text-lg font-bold text-ink flex items-center gap-1.5 justify-end">
                    <span className="w-2 h-2 rounded-full bg-brass animate-pulse"></span>
                    <span>{item.proposal_count} ({item.passed_gate_count} passed gate)</span>
                  </div>
                </div>

                <button
                  onClick={() => handleViewProposals(item.problem_id, item.title)}
                  className="px-5 py-2.5 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors shadow-sm text-xs flex items-center gap-1.5"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>View Proposals</span>
                </button>
              </div>

            </div>
          ))}
        </div>
      )}

      {/* Proposals Modal / Overlay */}
      {selectedProblemProposals !== null && (
        <div className="fixed inset-0 bg-ink/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-ivory border border-ink/20 rounded-2xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl space-y-6 max-h-[85vh] overflow-y-auto">
            
            <div className="flex justify-between items-center border-b border-ink/10 pb-4">
              <div>
                <span className="text-xs font-bold text-brass uppercase tracking-widest">Submitted Proposals</span>
                <h3 className="font-serif font-bold text-xl text-ink leading-tight">{selectedProblemTitle}</h3>
              </div>
              <button
                onClick={() => setSelectedProblemProposals(null)}
                className="text-ink-muted hover:text-ink font-bold text-lg"
              >
                ✕
              </button>
            </div>

            {selectedProblemProposals.length === 0 ? (
              <p className="text-xs text-ink-muted py-8 text-center">No proposals submitted for this problem yet.</p>
            ) : (
              <div className="space-y-3">
                {selectedProblemProposals.map((prop) => (
                  <div
                    key={prop.proposal_id}
                    className="p-4 rounded-xl border border-ink/10 bg-ivory hover:bg-ink/5 transition-all flex justify-between items-center gap-4"
                  >
                    <div>
                      <h4 className="font-serif font-bold text-base text-ink">{prop.solver_name}</h4>
                      <span className="text-xs text-forest font-semibold">
                        Gate Score: {prop.average_score} / 10 Avg
                      </span>
                    </div>

                    <button
                      onClick={() => {
                        setSelectedProblemProposals(null);
                        navigate(`/proposals/${prop.proposal_id}`);
                      }}
                      className="px-4 py-2 bg-brass text-ink font-semibold rounded-md hover:bg-brass-hover text-xs flex items-center gap-1.5"
                    >
                      <span>Review Details</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
};
