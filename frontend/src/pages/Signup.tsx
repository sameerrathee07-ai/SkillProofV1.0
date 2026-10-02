import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState<'poster' | 'solver'>('solver');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      await signup({ email, password, name, role });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto' }}>
      <div className="card" style={{ padding: '2rem' }}>
        <h1 className="page-title">Create account</h1>
        <p className="page-subtitle">Join SkillProof as a problem poster or solver</p>

        {error && (
          <div className="badge badge-error" style={{ width: '100%', justifyContent: 'center', marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="name" className="label">Name</label>
            <input
              id="name"
              type="text"
              className="input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoComplete="name"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="email" className="label">Email</label>
            <input
              id="email"
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="password" className="label">Password (min 8 characters)</label>
            <input
              id="password"
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="confirmPassword" className="label">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              className="input"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          <div className="mb-6">
            <label className="label">I want to</label>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <label style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', background: role === 'poster' ? 'var(--color-primary)' : 'var(--color-surface)', color: role === 'poster' ? 'white' : 'var(--color-text)', borderColor: role === 'poster' ? 'var(--color-primary)' : 'var(--color-border)' }}>
                <input
                  type="radio"
                  name="role"
                  value="poster"
                  checked={role === 'poster'}
                  onChange={() => setRole('poster')}
                  style={{ accentColor: 'var(--color-primary)' }}
                />
                <span>Post problems</span>
              </label>
              <label style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', background: role === 'solver' ? 'var(--color-primary)' : 'var(--color-surface)', color: role === 'solver' ? 'white' : 'var(--color-text)', borderColor: role === 'solver' ? 'var(--color-primary)' : 'var(--color-border)' }}>
                <input
                  type="radio"
                  name="role"
                  value="solver"
                  checked={role === 'solver'}
                  onChange={() => setRole('solver')}
                  style={{ accentColor: 'var(--color-primary)' }}
                />
                <span>Solve problems</span>
              </label>
            </div>
          </div>

          <button type="submit" className="btn btn-primary w-full" disabled={loading}>
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <p className="text-center text-sm text-secondary mt-6">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}