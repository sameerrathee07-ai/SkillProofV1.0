import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, CheckCircle2, ArrowRight, Building2, UserCheck } from 'lucide-react';

export const HeroLanding: React.FC = () => {
  const navigate = useNavigate();

  const demoProblems = [
    {
      id: 'demo-1',
      title: 'Automate Guest Check-In & Digital Room Key Dispatch',
      category: 'Hospitality',
      budget: '₹25,000 - ₹50,000',
      timeline: '3 weeks',
      description: 'Our 120-room hotel handles 50+ check-ins daily with 20-min lobby bottlenecks. Need automated QR check-in & room key generation.',
      proposals: 3
    },
    {
      id: 'demo-2',
      title: 'Automated Reconciliation Engine for UPI & Card POS',
      category: 'Financial Services',
      budget: '₹40,000 - ₹80,000',
      timeline: '4 weeks',
      description: 'End-of-day bank statement reconciliation across 4 retail outlets takes 3 hours manually. Need python auto-reconciliation script.',
      proposals: 5
    },
    {
      id: 'demo-3',
      title: 'Student Attendance Tracking via Smart Dynamic QR',
      category: 'Other',
      budget: '₹10,000 - ₹20,000',
      timeline: '1 week',
      description: 'Professors spend 10 mins per lecture calling roll across 80 students. Want time-expiring dynamic QR code system on smartphones.',
      proposals: 2
    }
  ];

  return (
    <div className="space-y-20 pb-16">
      {/* Hero Section */}
      <section className="relative pt-12 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brass/10 border border-brass/30 text-brass text-xs font-semibold uppercase tracking-wider mb-6">
          <ShieldCheck className="w-4 h-4" />
          <span>Mandatory Pitch Quality Gate</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-serif font-bold text-ink leading-tight max-w-4xl mx-auto">
          Stop filtering noise. Get <span className="text-brass italic">pre-vetted</span> solutions.
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-ink-muted max-w-2xl mx-auto leading-relaxed">
          Prove you understand the problem before posting. SkillProof blocks low-effort copy-pasted proposals using an automated 6-dimension quality gate.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row justify-center items-center gap-4">
          <button
            onClick={() => navigate('/signup')}
            className="w-full sm:w-auto px-8 py-4 bg-brass text-ink font-semibold rounded-md hover:bg-brass-hover transition-all shadow-md flex items-center justify-center gap-2 text-base"
          >
            <span>Get Started Now</span>
            <ArrowRight className="w-5 h-5" />
          </button>
          <button
            onClick={() => navigate('/problems')}
            className="w-full sm:w-auto px-8 py-4 bg-ivory border-2 border-ink text-ink font-semibold rounded-md hover:bg-ink/5 transition-all text-base"
          >
            Browse Open Problems
          </button>
        </div>

        {/* Hero Visual Mock */}
        <div className="mt-16 bg-ink text-ivory rounded-xl p-6 sm:p-8 shadow-2xl border border-brass/30 max-w-5xl mx-auto text-left relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-brass/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
          
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-6 border-b border-ivory/10">
            <div>
              <span className="text-xs font-semibold uppercase tracking-widest text-brass">Core Product Mechanic</span>
              <h3 className="text-2xl font-serif font-bold mt-1 text-ivory">The 5-Step Pitch Gate</h3>
            </div>
            <div className="flex items-center gap-2 bg-forest/30 text-forest-light px-3 py-1.5 rounded-md border border-forest/40 text-xs font-semibold">
              <CheckCircle2 className="w-4 h-4 text-forest" />
              <span>Gate Threshold: ≥ 6.0 / 10 Score Required</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mt-6">
            {[
              { step: '1', title: 'Solution Idea', detail: 'Word count & action verb check' },
              { step: '2', title: 'Target Pain', detail: 'Specific role & pain validation' },
              { step: '3', title: 'Cost Justification', detail: 'Numbers & ROI model' },
              { step: '4', title: 'Alternatives', detail: '2+ competitors & edge' },
              { step: '5', title: 'Solver Edge', detail: 'Experience & moat check' },
            ].map((s, idx) => (
              <div key={idx} className="bg-ink-light p-4 rounded-lg border border-ivory/10 flex flex-col justify-between">
                <div>
                  <span className="text-brass font-serif text-lg font-bold">0{s.step}</span>
                  <h4 className="font-semibold text-sm text-ivory mt-1">{s.title}</h4>
                  <p className="text-xs text-ivory/60 mt-1">{s.detail}</p>
                </div>
                <div className="mt-4 pt-2 border-t border-ivory/10 text-[10px] text-brass font-mono uppercase">
                  Rule-based
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Value Prop Columns */}
      <section className="bg-ink/5 py-16 px-4 sm:px-6 lg:px-8 border-y border-ink/10">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12">
          
          <div className="bg-ivory p-8 rounded-xl border border-ink/10 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-lg bg-brass/10 border border-brass/30 flex items-center justify-center text-brass">
              <Building2 className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-serif font-bold text-ink">For Problem Posters</h3>
            <p className="text-ink-muted leading-relaxed">
              Post real operational problems without fear of getting spammed by low-effort boilerplate templates. Receive only vetted proposals that have already passed our 6-dimension pitch gate.
            </p>
            <ul className="space-y-2 text-sm text-ink font-medium pt-2">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-forest" />
                <span>Zero copy-pasted spam in your inbox</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-forest" />
                <span>Standardized 5-step pitch breakdown</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-forest" />
                <span>Downloadable ReportLab PDF proposal packages</span>
              </li>
            </ul>
          </div>

          <div className="bg-ivory p-8 rounded-xl border border-ink/10 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-lg bg-forest/10 border border-forest/30 flex items-center justify-center text-forest">
              <UserCheck className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-serif font-bold text-ink">For Student & Early Solvers</h3>
            <p className="text-ink-muted leading-relaxed">
              Differentiate yourself based on problem comprehension, not just years of experience. Build a verifiable credibility track record that proves your technical competence.
            </p>
            <ul className="space-y-2 text-sm text-ink font-medium pt-2">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-forest" />
                <span>Guided 5-step pitch coach gives instant feedback</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-forest" />
                <span>Revision loop helps you fix weak dimensions</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-forest" />
                <span>Cumulative credibility score shown to clients</span>
              </li>
            </ul>
          </div>

        </div>
      </section>

      {/* Featured Problems Showcase */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 border-b border-ink/10 pb-4">
          <div>
            <span className="text-xs uppercase font-semibold text-brass tracking-widest">Active Listings</span>
            <h2 className="text-3xl font-serif font-bold text-ink mt-1">Live Operational Problems</h2>
          </div>
          <Link to="/problems" className="text-sm font-semibold text-brass hover:text-brass-hover flex items-center gap-1">
            <span>View All Problems</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {demoProblems.map((p) => (
            <div key={p.id} className="bg-ivory border border-ink/10 rounded-xl p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="px-2.5 py-1 rounded-full bg-forest-light text-forest text-xs font-semibold">
                    {p.category}
                  </span>
                  <span className="text-xs text-ink-muted font-medium">{p.proposals} proposals</span>
                </div>
                <h3 className="font-serif font-bold text-lg text-ink line-clamp-2 leading-snug">
                  {p.title}
                </h3>
                <p className="text-xs text-ink-muted line-clamp-3 leading-relaxed">
                  {p.description}
                </p>
              </div>

              <div className="pt-6 mt-6 border-t border-ink/10 flex justify-between items-center text-xs font-medium text-ink">
                <div>
                  <div className="font-semibold">{p.budget}</div>
                  <div className="text-ink-muted">{p.timeline}</div>
                </div>
                <button
                  onClick={() => navigate('/problems')}
                  className="px-3.5 py-2 bg-brass text-ink font-semibold rounded hover:bg-brass-hover transition-colors"
                >
                  Start Pitch
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
