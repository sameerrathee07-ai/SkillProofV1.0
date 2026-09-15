import React from 'react';
import { Link } from 'react-router-dom';
import { FileText } from 'lucide-react';

export const TermsOfService: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-8 font-sans text-ink">
      <div className="border-b border-ink/10 pb-6 flex items-center gap-4">
        <div className="p-3 bg-brass/10 text-brass rounded-xl">
          <FileText className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-serif font-bold">Terms of Service</h1>
          <p className="text-xs text-ink-muted">Effective Date: September 15, 2026</p>
        </div>
      </div>

      <div className="space-y-6 text-sm leading-relaxed text-ink/80">
        <section className="space-y-2">
          <h2 className="text-lg font-serif font-semibold text-ink">1. Platform Services</h2>
          <p>SkillProof connects problem posters with solvers through structured pitch evaluation frameworks. By creating an account, you agree to submit truthful, accurate, and non-infringing information.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-serif font-semibold text-ink">2. Automated Quality Evaluations & AI Disclosure</h2>
          <p>Pitches submitted to SkillProof undergo automated multidimensional quality scoring and validation to determine quality gate status (pass/fail). These algorithms evaluate clarity, feasibility, and market fit. Users may request manual secondary review if they believe an evaluation contains technical errors.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-serif font-semibold text-ink">3. Intellectual Property</h2>
          <p>Solvers retain full intellectual property rights to their submitted solution architectures until a formal transaction or partnership agreement is executed with a problem poster.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-serif font-semibold text-ink">4. Limitation of Liability</h2>
          <p>SkillProof provides platform services "as is" without warranty of any kind. Under no circumstances shall SkillProof be liable for indirect, incidental, or consequential damages.</p>
        </section>
      </div>

      <div className="pt-6 border-t border-ink/10 flex justify-between items-center text-xs text-ink-muted">
        <span>Legal inquiries: legal@skillproof.io</span>
        <Link to="/signup" className="text-brass font-semibold hover:underline">← Back to Signup</Link>
      </div>
    </div>
  );
};

export default TermsOfService;
