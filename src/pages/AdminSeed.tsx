import React, { useState } from 'react';
import { apiFetch } from '../lib/api';
import { Settings, Sparkles, CheckCircle2, AlertTriangle, Trash2, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const AdminSeed: React.FC = () => {
  const navigate = useNavigate();
  const [statusMsg, setStatusMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSeedProblems = async () => {
    setLoading(true);
    setStatusMsg('');
    setErrorMsg('');
    try {
      const res = await apiFetch('/admin/seed/problems', { method: 'POST' });
      setStatusMsg(res.message || 'Seeded demo problems!');
    } catch (err: any) {
      setErrorMsg(err.message || 'Seeding failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleSeedSolvers = async () => {
    setLoading(true);
    setStatusMsg('');
    setErrorMsg('');
    try {
      const res = await apiFetch('/admin/seed/solvers', { method: 'POST' });
      setStatusMsg(res.message || 'Seeded solver accounts!');
    } catch (err: any) {
      setErrorMsg(err.message || 'Seeding failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleFullDemoLoop = async () => {
    setLoading(true);
    setStatusMsg('');
    setErrorMsg('');
    try {
      const res = await apiFetch('/admin/seed/full-demo-loop', { method: 'POST' });
      setStatusMsg(`Full Demo Loop Executed! Created Proposal ID: ${res.proposal_id}`);
      setTimeout(() => {
        navigate(`/proposals/${res.proposal_id}`);
      }, 1500);
    } catch (err: any) {
      setErrorMsg(err.message || 'Demo loop failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleClearData = async () => {
    if (!window.confirm('Are you sure you want to clear all data in database?')) return;
    setLoading(true);
    setStatusMsg('');
    setErrorMsg('');
    try {
      const res = await apiFetch('/admin/clear', { method: 'DELETE' });
      setStatusMsg(res.message || 'Database cleared.');
    } catch (err: any) {
      setErrorMsg(err.message || 'Clear failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-12 space-y-8">
      
      <div className="border-b border-ink/10 pb-6 space-y-2">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-brass">
          <Settings className="w-4 h-4" />
          <span>Demo & Operational Tooling</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-ink">Admin Seed & Control Panel</h1>
        <p className="text-sm text-ink-muted">
          Pre-populate realistic problem listings, solver credibility records, and test the full 5-step quality gate loop with a single click.
        </p>
      </div>

      {statusMsg && (
        <div className="p-4 bg-forest-light border border-forest/40 text-forest text-xs font-semibold rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>{statusMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-brick-light border border-brick/40 text-brick text-xs font-semibold rounded-xl flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="bg-ivory border border-ink/10 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
        
        {/* Full Demo Loop Action */}
        <div className="bg-brass/10 border border-brass/30 p-6 rounded-xl space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-brass">
            <Sparkles className="w-4 h-4" />
            <span>Recommended For Hackathon Judges</span>
          </div>
          <h3 className="font-serif font-bold text-xl text-ink">One-Click Full Demo Loop</h3>
          <p className="text-xs text-ink-muted leading-relaxed">
            Seeds 5 problems, 3 solvers, 1 poster, generates a pitch submission, runs the quality gate scorer (7.3 score), and redirects straight to the Proposal Review page with downloadable PDF.
          </p>
          <button
            onClick={handleFullDemoLoop}
            disabled={loading}
            className="w-full py-3 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors shadow-md flex items-center justify-center gap-2 text-sm disabled:opacity-50"
          >
            <span>Execute Full Demo Loop</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <button
            onClick={handleSeedProblems}
            disabled={loading}
            className="p-4 bg-ivory border border-ink/20 hover:border-brass text-ink rounded-xl text-left font-medium space-y-1 transition-all"
          >
            <span className="font-bold text-sm block">Seed 5 Demo Problems</span>
            <span className="text-[11px] text-ink-muted block">Hospitality & Financial Services problems</span>
          </button>

          <button
            onClick={handleSeedSolvers}
            disabled={loading}
            className="p-4 bg-ivory border border-ink/20 hover:border-brass text-ink rounded-xl text-left font-medium space-y-1 transition-all"
          >
            <span className="font-bold text-sm block">Seed 3 Solver Accounts</span>
            <span className="text-[11px] text-ink-muted block">Sarah Chen, Raj Patel, Maya Sharma</span>
          </button>
        </div>

        <div className="pt-6 border-t border-ink/10 flex justify-between items-center">
          <span className="text-xs text-ink-muted font-medium">Clear Database State</span>
          <button
            onClick={handleClearData}
            disabled={loading}
            className="px-4 py-2.5 bg-brick text-ivory font-semibold rounded-lg hover:bg-brick-hover transition-colors text-xs flex items-center gap-1.5"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear All Data</span>
          </button>
        </div>

      </div>

    </div>
  );
};
