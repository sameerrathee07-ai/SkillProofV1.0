import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { TokenBalance, Package } from '../types'
import { useAuth } from '../hooks/useAuth'

export default function DashboardPage() {
  const [balance, setBalance] = useState<TokenBalance | null>(null)
  const [packages, setPackages] = useState<Package[]>([])
  const [buying, setBuying] = useState<string | null>(null)
  const { user } = useAuth()

  useEffect(() => {
    api.get('/tokens/balance').then(r => setBalance(r.data))
    api.get('/tokens/packages').then(r => setPackages(r.data))
  }, [])

  const purchase = async (pkgId: string) => {
    setBuying(pkgId)
    try {
      await api.post('/tokens/purchase', { package_id: pkgId })
      api.get('/tokens/balance').then(r => setBalance(r.data))
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Purchase failed')
    } finally {
      setBuying(null)
    }
  }

  if (!user || user.role !== 'solver') {
    return <div className="container">Only solvers have a dashboard.</div>
  }

  return (
    <div className="container">
      <h1 style={{ marginBottom: 24 }}>Dashboard</h1>
      <div className="card" style={{ marginBottom: 24 }}>
        <h3>Token Balance</h3>
        <div className="token-display" style={{ fontSize: 32, display: 'inline-block' }}>{balance?.balance || 0}</div>
        <p style={{ marginTop: 8, color: '#666' }}>Each pitch answer costs 2 tokens. Full pitch = 10 tokens.</p>
      </div>
      <div className="card">
        <h3 style={{ marginBottom: 16 }}>Buy Tokens (Mock)</h3>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          {packages.map(pkg => (
            <div key={pkg.id} className="card" style={{ flex: 1, minWidth: 200, textAlign: 'center', padding: 24 }}>
              <div style={{ fontSize: 18, fontWeight: 600 }}>{pkg.name}</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#0066cc', margin: '8px 0' }}>{pkg.tokens} tokens</div>
              <div style={{ fontSize: 18, marginBottom: 16 }}>Rs {pkg.price_rs}</div>
              <button 
                onClick={() => purchase(pkg.id)} 
                disabled={buying === pkg.id}
                style={{ width: '100%' }}
              >
                {buying === pkg.id ? 'Processing...' : 'Buy'}
              </button>
            </div>
          ))}
        </div>
      </div>
      <Link to="/my-proposals"><button className="btn-secondary" style={{ marginTop: 24 }}>My Proposals</button></Link>
    </div>
  )
}