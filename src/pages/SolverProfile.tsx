import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import { ShieldCheck } from 'lucide-react';

export const SolverProfile: React.FC = () => {
  const { solverId } = useParams<{ solverId: string }>();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (solverId) fetchProfile();
  }, [solverId]);

  const fetchProfile = async () => {
    try {
      const data = await apiFetch(`/solver/${solverId}`);
      setProfile(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load solver profile.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brass"></div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <div className="p-4 bg-brick-light text-brick rounded-lg text-xs font-semibold">
          {error || 'Solver profile not found.'}
        </div>
      </div>
    );
  }

  const passRate = profile.total_proposals > 0
    ? Math.round((profile.passed_first_attempt / profile.total_proposals) * 100)
    : 0;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      
      {/* Header Profile Card */}
      <div className="bg-ivory border border-ink/10 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
        
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-ink text-ivory flex items-center justify-center font-serif text-3xl font-bold shadow-md">
              {profile.name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl sm:text-3xl font-serif font-bold text-ink">{profile.name}</h1>
                <ShieldCheck className="w-5 h-5 text-forest" />
              </div>
              <p className="text-xs text-ink-muted mt-1">Verified SkillProof Solver Profile</p>
            </div>
          </div>

          {/* Large Credibility Score Badge */}
          <div className="bg-forest-light border border-forest/30 p-4 rounded-xl text-center min-w-[140px]">
            <span className="text-[10px] font-bold uppercase tracking-wider text-forest block">Credibility Score</span>
            <div className="text-3xl font-serif font-extrabold text-forest mt-0.5">
              {profile.credibility_score} <span className="text-xl font-normal">/ 5.0</span>
            </div>
            <span className="text-[10px] text-forest/80 font-medium block mt-0.5">
              Based on {profile.total_proposals} submission{profile.total_proposals === 1 ? '' : 's'}
            </span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-ink/10">
          <div className="bg-ink/5 p-4 rounded-xl border border-ink/10 space-y-1">
            <span className="text-xs text-ink-muted font-medium">1st Attempt Pass Rate</span>
            <div className="text-xl font-bold text-ink">{passRate}%</div>
            <span className="text-[10px] text-forest font-semibold">{profile.passed_first_attempt} / {profile.total_proposals} passed</span>
          </div>

          <div className="bg-ink/5 p-4 rounded-xl border border-ink/10 space-y-1">
            <span className="text-xs text-ink-muted font-medium">Avg Dimension Score</span>
            <div className="text-xl font-bold text-ink">{profile.average_score_across_all} / 10</div>
            <span className="text-[10px] text-brass font-semibold">Quality gate median</span>
          </div>

          <div className="bg-ink/5 p-4 rounded-xl border border-ink/10 space-y-1">
            <span className="text-xs text-ink-muted font-medium">Categories Expertise</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {profile.categories.map((cat: string) => (
                <span key={cat} className="px-2 py-0.5 rounded bg-brass/20 text-ink text-[10px] font-bold">
                  {cat}
                </span>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* Past Submissions History */}
      <div className="bg-ivory border border-ink/10 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
        <h3 className="font-serif font-bold text-xl text-ink">Submission History & Track Record</h3>
        
        {profile.recent_submissions.length === 0 ? (
          <p className="text-xs text-ink-muted italic">No past submissions yet.</p>
        ) : (
          <div className="space-y-3">
            {profile.recent_submissions.map((sub: any) => (
              <div
                key={sub.proposal_id}
                className="p-4 rounded-xl border border-ink/10 bg-ivory hover:bg-ink/5 transition-all flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3"
              >
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-brass">{sub.category}</span>
                  <h4 className="font-serif font-bold text-base text-ink">{sub.problem_title}</h4>
                </div>

                <div className="flex items-center gap-3 text-xs font-semibold">
                  <span className="font-mono text-ink">{sub.score} / 10 Score</span>
                  <span className={`px-2.5 py-1 rounded-full text-[10px] uppercase tracking-wider ${
                    sub.status === 'submitted' ? 'bg-forest-light text-forest' : 'bg-brick-light text-brick'
                  }`}>
                    {sub.status === 'submitted' ? 'Passed Gate ✓' : 'Needs Work'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};
