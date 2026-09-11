import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import { Building2, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';

export const PostProblemForm: React.FC = () => {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Hospitality');
  const [budgetRange, setBudgetRange] = useState('');
  const [timeline, setTimeline] = useState('');

  const [serverError, setServerError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [loading, setLoading] = useState(false);

  // Client side validation heuristics
  const words = description.trim().split(/\s+/).filter(Boolean);
  const wordCount = words.length;
  const hasMinWords = wordCount >= 15;
  
  const VERBS = ["helps", "makes", "builds", "creates", "connects", "automates", "saves", "reduces", "lets", "allows", "turns", "replaces", "tracks", "manages", "improves", "solves", "need", "needs", "want", "wants", "require", "requires"];
  const hasVerb = words.some(w => VERBS.includes(w.toLowerCase().replace(/[^a-z]/g, '')));

  const hasCurrency = /[$€£₹¥]|(?:rs|rupees|dollars|inr|usd|eur|lakh|k)\b/i.test(budgetRange) && /\d+/.test(budgetRange);
  const hasTimelineRef = /week|month|day|year|date|by|deadline|quarter|\d+/i.test(timeline);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError('');
    setSuccessMsg('');

    if (!hasMinWords) {
      setServerError('Description must be at least 15 words.');
      return;
    }
    if (!hasVerb) {
      setServerError('Description must contain a clear action verb explaining what you need built or solved.');
      return;
    }
    if (!hasCurrency) {
      setServerError('Budget range must include a currency symbol (₹, $, etc.) and a number.');
      return;
    }
    if (!hasTimelineRef) {
      setServerError('Timeline must specify duration or target date.');
      return;
    }

    setLoading(true);

    try {
      await apiFetch('/problems', {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim() || undefined,
          description,
          category,
          budgetRange,
          timeline,
        }),
      });

      setSuccessMsg('Your problem listing is now live! Solvers will be gated before submitting.');
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err: any) {
      setServerError(err.message || 'Failed to post problem.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-12 space-y-8">
      <div className="border-b border-ink/10 pb-6 space-y-2">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-brass">
          <Building2 className="w-4 h-4" />
          <span>Problem Poster Flow</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-ink">Describe Your Operational Problem</h1>
        <p className="text-sm text-ink-muted leading-relaxed">
          SkillProof requires problems to have clear context, budget, and timeline so solvers can craft targeted pitches.
        </p>
      </div>

      {serverError && (
        <div className="p-4 bg-brick-light border border-brick/40 text-brick text-xs font-semibold rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{serverError}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 bg-forest-light border border-forest/40 text-forest text-xs font-semibold rounded-lg flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-ivory border border-ink/10 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
        
        <div>
          <label className="block text-xs font-bold uppercase text-ink-muted tracking-wider mb-1">
            Problem Title / Headline
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Automate Guest Check-In & Digital Key Generation"
            className="w-full px-4 py-2.5 rounded-lg border border-ink/20 bg-ivory text-ink focus:outline-none focus:ring-2 focus:ring-brass text-sm font-medium"
          />
        </div>

        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="block text-xs font-bold uppercase text-ink-muted tracking-wider">
              Detailed Description (≥15 Words)
            </label>
            <div className="text-xs font-mono text-ink-muted">
              Word Count: <span className={hasMinWords ? 'text-forest font-bold' : 'text-brick'}>{wordCount}</span> / 15
            </div>
          </div>
          <textarea
            required
            rows={5}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Our 120-room hotel checks in 50+ guests daily, causing 20-minute lobby bottlenecks. We need an automated mobile or kiosk system with QR check-in and digital room key dispatch..."
            className="w-full px-4 py-3 rounded-lg border border-ink/20 bg-ivory text-ink focus:outline-none focus:ring-2 focus:ring-brass text-sm font-medium leading-relaxed"
          />

          {/* Instant Validation Feedback */}
          <div className="mt-2 flex items-center gap-4 text-xs font-semibold">
            <span className={`flex items-center gap-1 ${hasMinWords ? 'text-forest' : 'text-brick'}`}>
              {hasMinWords ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
              <span>At least 15 words</span>
            </span>
            <span className={`flex items-center gap-1 ${hasVerb ? 'text-forest' : 'text-brick'}`}>
              {hasVerb ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
              <span>Contains action verb</span>
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-xs font-bold uppercase text-ink-muted tracking-wider mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-ink/20 bg-ivory text-ink focus:outline-none focus:ring-2 focus:ring-brass text-sm font-medium"
            >
              <option value="Hospitality">Hospitality</option>
              <option value="Financial Services">Financial Services</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-ink-muted tracking-wider mb-1">Budget Range</label>
            <input
              type="text"
              required
              value={budgetRange}
              onChange={(e) => setBudgetRange(e.target.value)}
              placeholder="e.g. ₹25,000 - ₹50,000"
              className="w-full px-3.5 py-2.5 rounded-lg border border-ink/20 bg-ivory text-ink focus:outline-none focus:ring-2 focus:ring-brass text-sm font-medium"
            />
            {budgetRange && (
              <span className={`text-[11px] font-semibold mt-1 flex items-center gap-1 ${hasCurrency ? 'text-forest' : 'text-brick'}`}>
                {hasCurrency ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                <span>Currency symbol + numbers</span>
              </span>
            )}
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-ink-muted tracking-wider mb-1">Timeline</label>
            <input
              type="text"
              required
              value={timeline}
              onChange={(e) => setTimeline(e.target.value)}
              placeholder="e.g. 3 weeks or Sept 30"
              className="w-full px-3.5 py-2.5 rounded-lg border border-ink/20 bg-ivory text-ink focus:outline-none focus:ring-2 focus:ring-brass text-sm font-medium"
            />
            {timeline && (
              <span className={`text-[11px] font-semibold mt-1 flex items-center gap-1 ${hasTimelineRef ? 'text-forest' : 'text-brick'}`}>
                {hasTimelineRef ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                <span>Duration / date reference</span>
              </span>
            )}
          </div>
        </div>

        <div className="pt-4 border-t border-ink/10 flex justify-between items-center">
          <div className="text-xs text-ink-muted font-medium">
            Posting Cost: <span className="font-bold text-brass">5 Tokens</span> (Deducted on publication)
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors shadow-sm disabled:opacity-50 flex items-center gap-2"
          >
            <span>{loading ? 'Publishing...' : 'Publish Listing'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </form>
    </div>
  );
};
