import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../lib/auth-context';
import { apiFetch } from '../lib/api';
import { Eye, EyeOff } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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
          role: 'solver',
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
    setLoading(true);

    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
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
      setError(err.message || 'Invalid email or password.');
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
          <h2 className="text-3xl font-serif font-bold text-ink">Welcome Back</h2>
          <p className="text-xs text-ink-muted">Sign in to your SkillProof account</p>
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
          />
        </div>

        <div className="relative flex items-center justify-center">
          <div className="border-t border-ink/10 w-full"></div>
          <span className="bg-ivory px-3 text-[10px] uppercase tracking-wider font-semibold text-ink-muted shrink-0">
            or sign in with email
          </span>
          <div className="border-t border-ink/10 w-full"></div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-sm font-medium">
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
                placeholder="Enter password"
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
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <div className="text-center pt-4 border-t border-ink/10 text-xs text-ink-muted">
          Don't have an account?{' '}
          <Link to="/signup" className="text-brass font-bold hover:underline">
            Sign up
          </Link>
        </div>

      </div>
    </div>
  );
};

