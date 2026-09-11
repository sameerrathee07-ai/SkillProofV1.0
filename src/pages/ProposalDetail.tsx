import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import { Download, Mail, CheckCircle2, ShieldCheck, Check } from 'lucide-react';

export const ProposalDetail: React.FC = () => {
  const { proposalId } = useParams<{ proposalId: string }>();
  const [proposal, setProposal] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (proposalId) fetchProposal();
  }, [proposalId]);

  const fetchProposal = async () => {
    try {
      const data = await apiFetch(`/proposals/${proposalId}`);
      setProposal(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load proposal details.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    const token = localStorage.getItem('skillproof_token');
    const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
    
    fetch(`${apiUrl}/proposals/${proposalId}/pdf`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `proposal_${proposal?.solver_name.replace(' ', '_')}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      })
      .catch(() => alert('Failed to download PDF.'));
  };

  const handleCopyEmail = () => {
    if (proposal?.solver_name) {
      navigator.clipboard.writeText(`${proposal.solver_name.toLowerCase().replace(' ', '.')}@solver.com`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brass"></div>
      </div>
    );
  }

  if (error || !proposal) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <div className="p-4 bg-brick-light text-brick rounded-lg text-xs font-semibold">
          {error || 'Proposal not found.'}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      
      {/* Top Banner & Header */}
      <div className="bg-ivory border border-ink/10 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
        
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-ink/10 pb-6">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-brass mb-1">
              <ShieldCheck className="w-4 h-4" />
              <span>Vetted Proposal Package</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-ink">{proposal.problem_title}</h1>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleDownloadPdf}
              className="px-4 py-2.5 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors shadow-sm flex items-center gap-2 text-xs"
            >
              <Download className="w-4 h-4" />
              <span>Download PDF</span>
            </button>

            <button
              onClick={handleCopyEmail}
              className="px-4 py-2.5 bg-ivory border border-ink text-ink font-semibold rounded-lg hover:bg-ink/5 transition-colors flex items-center gap-2 text-xs"
            >
              {copied ? <Check className="w-4 h-4 text-forest" /> : <Mail className="w-4 h-4" />}
              <span>{copied ? 'Email Copied!' : 'Contact Solver'}</span>
            </button>
          </div>
        </div>

        {/* Solver Credibility Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-ink/5 p-4 rounded-xl border border-ink/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-brass text-ink font-bold flex items-center justify-center font-serif text-lg">
              {proposal.solver_name.charAt(0)}
            </div>
            <div>
              <Link to={`/solver/${proposal.solver_id}`} className="font-serif font-bold text-lg text-ink hover:text-brass transition-colors">
                {proposal.solver_name}
              </Link>
              <div className="text-xs text-ink-muted flex items-center gap-2 mt-0.5">
                <span>⭐ Credibility Score: <strong className="text-forest">{proposal.solver_credibility_score} / 5.0</strong></span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-forest-light text-forest px-3.5 py-1.5 rounded-full border border-forest/30 text-xs font-bold">
            <CheckCircle2 className="w-4 h-4" />
            <span>Passed Quality Gate ({proposal.average_score} / 10 Avg)</span>
          </div>
        </div>

      </div>

      {/* Dimension Scores Card */}
      <div className="bg-ivory border border-ink/10 rounded-2xl p-6 sm:p-8 shadow-sm space-y-4">
        <h3 className="font-serif font-bold text-xl text-ink">Score Breakdown Across 6 Dimensions</h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Object.entries(proposal.dimension_scores).map(([dim, score]: [string, any]) => (
            <div key={dim} className="bg-ivory border border-ink/10 p-3.5 rounded-lg space-y-1.5">
              <div className="flex justify-between text-xs font-bold text-ink uppercase tracking-wider">
                <span>{dim.replace('_', ' ')}</span>
                <span className="text-brass font-extrabold">{score} / 10</span>
              </div>
              <div className="w-full bg-ink/10 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-brass h-full transition-all"
                  style={{ width: `${(score / 10) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full 5-Step Pitch Responses */}
      <div className="bg-ivory border border-ink/10 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
        <h3 className="font-serif font-bold text-xl text-ink border-b border-ink/10 pb-4">Full 5-Step Pitch Outline</h3>
        
        <div className="space-y-6">
          {[
            { label: 'Step 1 — Solution Approach', val: proposal.pitch_responses.step1 },
            { label: 'Step 2 — Target Role & Pain Point', val: proposal.pitch_responses.step2 },
            { label: 'Step 3 — Cost & Value Justification', val: proposal.pitch_responses.step3 },
            { label: 'Step 4 — Alternative Approaches & Edge', val: proposal.pitch_responses.step4 },
            { label: 'Step 5 — Solver Background & Advantage', val: proposal.pitch_responses.step5 },
          ].map((s, idx) => (
            <div key={idx} className="space-y-1.5">
              <span className="text-xs font-bold uppercase tracking-widest text-brass block">
                {s.label}
              </span>
              <p className="text-sm text-ink leading-relaxed bg-ink/5 p-4 rounded-xl border border-ink/10 font-medium">
                {s.val || 'Not specified.'}
              </p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
