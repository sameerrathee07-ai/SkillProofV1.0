import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

function AuthForm({ mode }: { mode: 'login' | 'signup' }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [role, setRole] = useState<'poster' | 'solver'>('solver')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, signup } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(email, password, role)
      } else {
        await signup(email, password, name, role)
      }
      navigate(mode === 'login' ? '/' : '/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ maxWidth: 400, margin: '60px auto' }}>
      <h2 style={{ marginBottom: 24, textAlign: 'center' }}>{mode === 'login' ? 'Login' : 'Sign Up'}</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        {mode === 'signup' && (
          <>
            <div className="form-group">
              <label>Name</label>
              <input type="text" value={name} onChange={e => setName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>I am a</label>
              <select value={role} onChange={e => setRole(e.target.value as 'poster' | 'solver')}> 
                <option value="solver">Solver (pitch solutions)</option>
                <option value="poster">Problem Poster (post problems)</option>
              </select>
            </div>
          </>
        )}
        <div className="form-group">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Password (min 8 chars)</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} />
        </div>
        <button type="submit" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
          {loading ? '...' : (mode === 'login' ? 'Login' : 'Sign Up')}
        </button>
      </form>
      <p style={{ marginTop: 16, textAlign: 'center', color: '#666' }}>
        {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}
        <Link to={mode === 'login' ? '/signup' : '/login'} style={{ marginLeft: 8 }}>
          {mode === 'login' ? 'Sign Up' : 'Login'}
        </Link>
      </p>
    </div>
  )
}

export default function LoginPage() {
  return <AuthForm mode="login" />
}

export function SignupPage() {
  return <AuthForm mode="signup" />
}