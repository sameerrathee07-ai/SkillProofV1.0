import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../lib/auth-context';
import { apiFetch } from '../lib/api';
import { Eye, EyeOff, Building2, UserCheck } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';

export const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [fullName, setFullName] = useState('');
  const [organization, setOrganization] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'poster' | 'solver'>('solver');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGoogleSuccess = async (credentialResponse: any) => {
    if (!credentialResponse.credential) return;
    setError('');
    setLoading(true);
    try {
      const data = await apiFetch('/auth/google', {
        method: 'POST',
        body: JSON.stringify({
          id_token: credentialResponse.credential,
          role,
        }),
      });

      login(data.access_token, {
        id: data.user_id,
        email: data.email,
        fullName: data.fullName,
        role: data.role,
      });

      if (data.role === 'poster') {
        navigate('/dashboard');
      } else {
        navigate('/problems');
      }
    } catch (err: any) {
      setError(err.message || 'Google Sign-In failed.');
    } finally {
      setLoading(false);
    }
  };


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (fullName.trim().length < 2) {
      setError('Full Name must be at least 2 characters.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setLoading(true);

    try {
      const data = await apiFetch('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({
          fullName,
          organization,
          email,
          password,
          role,
        }),
      });

      login(data.access_token, {
        id: data.user_id,
        email: data.email,
        fullName: data.fullName,
        role: data.role,
      });

      if (data.role === 'poster') {
        navigate('/dashboard');
      } else {
        navigate('/problems');
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="bg-ivory border border-ink/10 rounded-2xl p-8 sm:p-10 shadow-lg max-w-md w-full space-y-6">

        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-ink text-ivory flex items-center justify-center font-serif text-2xl font-bold mx-auto shadow-md">
            S<span className="text-brass">P</span>
          </div>
          <h2 className="text-3xl font-serif font-bold text-ink">Create Account</h2>
          <p className="text-xs text-ink-muted">Join SkillProof to post problems or pitch vetted solutions</p>
        </div>

        {error && (
          <div className="p-3 bg-brick-light border border-brick/30 text-brick text-xs font-semibold rounded-md">
            {error}
          </div>
        )}

        {/* Google Sign-In */}
        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError('Google Sign-In failed or was closed.')}
            theme="outline"
            shape="rectangular"
            width="100%"
          />
        </div>

        <div className="relative flex items-center justify-center">
          <div className="border-t border-ink/10 w-full"></div>
          <span className="bg-ivory px-3 text-[10px] uppercase tracking-wider font-semibold text-ink-muted shrink-0">
            or sign up with email
          </span>
          <div className="border-t border-ink/10 w-full"></div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-sm font-medium">

          {/* Role Selector */}
          <div className="space-y-1">
            <label className="block text-xs font-semibold uppercase text-ink-muted tracking-wider">Select Your Role</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setRole('solver')}
                className={`p-3 rounded-lg border flex flex-col items-center gap-1.5 transition-all ${role === 'solver'
                  ? 'border-brass bg-brass/10 text-ink shadow-sm'
                  : 'border-ink/10 bg-ivory text-ink-muted hover:border-ink/20'
                  }`}
              >
                <UserCheck className={`w-5 h-5 ${role === 'solver' ? 'text-brass' : ''}`} />
                <span className="text-xs font-bold">Solver</span>
                <span className="text-[10px] text-ink-muted">Pitch solutions</span>
              </button>

              <button
                type="button"
                onClick={() => setRole('poster')}
                className={`p-3 rounded-lg border flex flex-col items-center gap-1.5 transition-all ${role === 'poster'
                  ? 'border-brass bg-brass/10 text-ink shadow-sm'
                  : 'border-ink/10 bg-ivory text-ink-muted hover:border-ink/20'
                  }`}
              >
                <Building2 className={`w-5 h-5 ${role === 'poster' ? 'text-brass' : ''}`} />
                <span className="text-xs font-bold">Problem Poster</span>
                <span className="text-[10px] text-ink-muted">Receive proposals</span>
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-ink-muted tracking-wider mb-1">Full Name</label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Sarah Chen"
              className="w-full px-3.5 py-2.5 rounded-md border border-ink/20 bg-ivory text-ink focus:outline-none focus:ring-2 focus:ring-brass"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-ink-muted tracking-wider mb-1">Organization / School (Optional)</label>
            <input
              type="text"
              value={organization}
              onChange={(e) => setOrganization(e.target.value)}
              placeholder="IIT Bombay or Grand Hyatt"
              className="w-full px-3.5 py-2.5 rounded-md border border-ink/20 bg-ivory text-ink focus:outline-none focus:ring-2 focus:ring-brass"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-ink-muted tracking-wider mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="sarah@example.com"
              className="w-full px-3.5 py-2.5 rounded-md border border-ink/20 bg-ivory text-ink focus:outline-none focus:ring-2 focus:ring-brass"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-ink-muted tracking-wider mb-1">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
                className="w-full px-3.5 py-2.5 rounded-md border border-ink/20 bg-ivory text-ink focus:outline-none focus:ring-2 focus:ring-brass pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-3 text-ink-muted hover:text-ink"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-brass text-ink font-semibold rounded-md hover:bg-brass-hover transition-colors shadow-sm mt-4 disabled:opacity-50"
          >
            {loading ? 'Creating Account...' : 'Create SkillProof Account'}
          </button>
        </form>

        <div className="text-center pt-4 border-t border-ink/10 text-xs text-ink-muted">
          Already have an account?{' '}
          <Link to="/login" className="text-brass font-bold hover:underline">
            Sign in
          </Link>
        </div>

      </div>
    </div>
  );
};