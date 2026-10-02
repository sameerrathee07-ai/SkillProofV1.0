import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { tokensApi } from '../utils/api';
import type { TokenBalance, TokenPackage } from '../types';

export default function Tokens() {
  const { user } = useAuth();
  const [balance, setBalance] = useState<TokenBalance | null>(null);
  const [packages, setPackages] = useState<TokenPackage[]>([]);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [balanceRes, packagesRes] = await Promise.all([
          tokensApi.balance(),
          tokensApi.packages(),
        ]);
        setBalance(balanceRes.data);
        setPackages(packagesRes.data);
      } catch (err) {
        console.error('Failed to load tokens:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handlePurchase = async (pkg: TokenPackage) => {
    setPurchasing(pkg.id);
    try {
      const idempotencyKey = `purchase_${pkg.id}_${Date.now()}`;
      const res = await tokensApi.purchase(pkg.id, idempotencyKey);
      if (res.data.success) {
        setBalance({ balance: res.data.new_balance });
        alert(`Successfully purchased ${pkg.tokens} tokens for Rs ${pkg.price_rs}!`);
      } else {
        alert('Purchase failed. Please try again.');
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Purchase failed');
    } finally {
      setPurchasing(null);
    }
  };

  if (loading) {
    return <div className="text-center text-secondary py-8">Loading...</div>;
  }

  return (
    <div style={{ maxWidth: '800px' }}>
      <div className="page-header">
        <h1 className="page-title">Token Balance</h1>
        <p className="page-subtitle">Each pitch answer costs 2 tokens. A full 5-step pitch costs 10 tokens.</p>
      </div>

      <div className="card mb-6" style={{ padding: '2rem', textAlign: 'center' }}>
        <div className="text-sm text-secondary mb-1">Current Balance</div>
        <div className="text-5xl font-bold text-primary">{balance?.balance || 0}</div>
        <div className="text-sm text-secondary mt-2">
          {user?.role === 'solver' ? 'Sign up bonus: 20 tokens (2 full pitches)' : 'Problem posters do not need tokens'}
        </div>
      </div>

      <div className="card" style={{ padding: '1.5rem' }}>
        <h3 className="font-semibold mb-4">Buy Token Packages</h3>
        <div className="grid grid-3">
          {packages.map(pkg => (
            <div key={pkg.id} className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', border: purchasing === pkg.id ? '2px solid var(--color-primary)' : '1px solid var(--color-border)' }}>
              <div className="text-center mb-4">
                <div className="text-3xl font-bold text-primary">Rs {pkg.price_rs}</div>
                <div className="text-secondary">{pkg.name}</div>
              </div>
              <div className="text-center mb-4">
                <div className="text-2xl font-bold">{pkg.tokens} tokens</div>
                <div className="text-sm text-secondary">{Math.floor(pkg.tokens / 10)} full pitches</div>
              </div>
              <button
                onClick={() => handlePurchase(pkg)}
                disabled={purchasing !== null}
                className="btn btn-primary w-full"
              >
                {purchasing === pkg.id ? 'Processing...' : `Buy for Rs ${pkg.price_rs}`}
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="card mt-6" style={{ padding: '1.5rem' }}>
        <h3 className="font-semibold mb-3">How Tokens Work</h3>
        <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
          <li>• <strong>Signup bonus:</strong> 20 free tokens (enough for 2 complete pitches)</li>
          <li>• <strong>Per answer:</strong> 2 tokens deducted only when your answer passes validation</li>
          <li>• <strong>Rejected answers:</strong> No tokens charged</li>
          <li>• <strong>Full pitch:</strong> 5 steps × 2 tokens = 10 tokens total</li>
          <li>• <strong>Revisions:</strong> Only re-edited steps are re-validated and charged</li>
          <li>• <strong>Mock purchases:</strong> Token packages are simulated (no real payment)</li>
        </ul>
      </div>
    </div>
  );
}