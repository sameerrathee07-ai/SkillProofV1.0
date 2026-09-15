import React from 'react';
import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';

export const PrivacyPolicy: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-8 font-sans text-ink">
      <div className="border-b border-ink/10 pb-6 flex items-center gap-4">
        <div className="p-3 bg-brass/10 text-brass rounded-xl">
          <Shield className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-serif font-bold">Privacy Policy</h1>
          <p className="text-xs text-ink-muted">Last Updated: September 15, 2026 | GDPR Article 13/14 & CCPA Compliant</p>
        </div>
      </div>

      <div className="space-y-6 text-sm leading-relaxed text-ink/80">
        <section className="space-y-2">
          <h2 className="text-lg font-serif font-semibold text-ink">1. Information We Collect</h2>
          <p>SkillProof collects personal data necessary to provide our problem-solving platform, including:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Account Information:</strong> Full name, email address, organization name, and role preference (Solver or Poster).</li>
            <li><strong>OAuth Data:</strong> Profile name and email when signing up via Google Sign-In.</li>
            <li><strong>Submission Data:</strong> Pitch responses, problem descriptions, and quality gate evaluations.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-serif font-semibold text-ink">2. How Data is Used</h2>
          <p>We process your personal information strictly for authentication, platform security, proposal matching, and generating quality evaluations via automated pitch analysis models.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-serif font-semibold text-ink">3. Your Data Rights (GDPR & CCPA)</h2>
          <p>Under GDPR Article 17 and CCPA §1798.105, you have the right to request access to, export, or complete deletion of your personal account data at any time through our automated support channels or your profile setting dashboard.</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-serif font-semibold text-ink">4. Third-Party Services</h2>
          <p>We do not sell personal information to third parties. Data is shared only with sub-processors strictly essential for operating the platform (e.g., authentication providers and cloud hosting services).</p>
        </section>
      </div>

      <div className="pt-6 border-t border-ink/10 flex justify-between items-center text-xs text-ink-muted">
        <span>Questions? Contact privacy@skillproof.io</span>
        <Link to="/signup" className="text-brass font-semibold hover:underline">← Back to Signup</Link>
      </div>
    </div>
  );
};

export default PrivacyPolicy;
