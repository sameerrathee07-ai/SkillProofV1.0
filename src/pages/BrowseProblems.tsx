import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import { Filter, ArrowRight, ShieldCheck } from 'lucide-react';

interface Problem {
  problem_id: string;
  poster_id: string;
  poster_name: string;
  title: string;
  description: string;
  category: string;
  budgetRange: string;
  timeline: string;
  status: string;
  created_at: string;
  proposal_count: number;
  passed_gate_count: number;
}

export const BrowseProblems: React.FC = () => {
  const navigate = useNavigate();
  const [problems, setProblems] = useState<Problem[]>([]);
  const [category, setCategory] = useState<string>('All');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchProblems();
  }, [category]);

  const fetchProblems = async () => {
    setLoading(true);
    setError('');
    try {
      const url = `/problems?category=${encodeURIComponent(category)}`;
      const data = await apiFetch(url);
      setProblems(data.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load open problems.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Header & Category Filter Bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-ink/10 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-brass mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Vetted Problem Pool</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-serif font-bold text-ink">Browse Open Operational Problems</h1>
          <p className="text-sm text-ink-muted mt-1">Select a problem to initiate the 5-Step Pitch Quality Gate.</p>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <Filter className="w-4 h-4 text-ink-muted mr-1" />
          {['All', 'Hospitality', 'Financial Services', 'Other'].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                category === cat
                  ? 'bg-brass text-ink shadow-sm'
                  : 'bg-ivory border border-ink/20 text-ink-muted hover:border-ink/40'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-16 space-y-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brass mx-auto"></div>
          <p className="text-xs text-ink-muted">Loading open problems...</p>
        </div>
      ) : error ? (
        <div className="p-4 bg-brick-light text-brick rounded-lg text-xs font-semibold border border-brick/30 text-center">
          {error}
        </div>
      ) : problems.length === 0 ? (
        <div className="text-center py-16 bg-ivory border border-dashed border-ink/20 rounded-2xl p-8 space-y-3">
          <p className="text-lg font-serif font-bold text-ink">No open problems found in this category.</p>
          <p className="text-xs text-ink-muted">Check back soon or switch categories.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {problems.map((p) => (
            <div
              key={p.problem_id}
              className="bg-ivory border border-ink/10 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-6"
            >
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="px-2.5 py-1 rounded-full bg-forest-light text-forest text-xs font-bold tracking-wide">
                    {p.category}
                  </span>
                  <span className="text-xs text-ink-muted font-medium">
                    {p.proposal_count} proposals ({p.passed_gate_count} passed)
                  </span>
                </div>

                <h3 className="font-serif font-bold text-xl text-ink leading-snug">
                  {p.title}
                </h3>

                <p className="text-xs text-ink-muted line-clamp-3 leading-relaxed">
                  {p.description}
                </p>
              </div>

              <div className="space-y-4 pt-4 border-t border-ink/10">
                <div className="grid grid-cols-2 gap-2 text-xs font-medium">
                  <div>
                    <span className="text-[10px] text-ink-muted uppercase block">Budget</span>
                    <span className="font-bold text-ink">{p.budgetRange}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-ink-muted uppercase block">Timeline</span>
                    <span className="font-bold text-ink">{p.timeline}</span>
                  </div>
                </div>

                <button
                  onClick={() => navigate(`/pitch/${p.problem_id}`)}
                  className="w-full py-3 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors shadow-sm flex items-center justify-center gap-2 text-sm"
                >
                  <span>Start My Pitch</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
};
