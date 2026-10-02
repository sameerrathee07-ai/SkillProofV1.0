import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', roles: ['poster', 'solver'] },
    { path: '/problems', label: 'Browse Problems', roles: ['poster', 'solver'] },
    { path: '/problems/post', label: 'Post Problem', roles: ['poster'] },
    { path: '/inbox', label: 'My Inbox', roles: ['poster'] },
    { path: '/tokens', label: 'Tokens', roles: ['solver'] },
  ];

  const filteredNav = navItems.filter(item => item.roles.includes(user?.role || ''));

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ background: 'var(--color-surface)', borderBottom: '1px solid var(--color-border)', position: 'sticky', top: 0, zIndex: 100 }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '64px' }}>
          <Link to="/dashboard" style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-primary)', textDecoration: 'none' }}>
            SkillProof
          </Link>
          <nav style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            {filteredNav.map(item => (
              <Link
                key={item.path}
                to={item.path}
                className={location.pathname === item.path ? 'font-semibold text-primary' : 'text-secondary hover:text-primary'}
                style={{ fontSize: '0.875rem', fontWeight: 500, textDecoration: 'none' }}
              >
                {item.label}
              </Link>
            ))}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', paddingLeft: '1rem', borderLeft: '1px solid var(--color-border)' }}>
              <span className="text-sm text-secondary">{user?.name}</span>
              <span className={`badge ${user?.role === 'poster' ? 'badge-info' : 'badge-success'}`}>{user?.role}</span>
              <button onClick={logout} className="btn btn-secondary text-sm">Logout</button>
            </div>
          </nav>
        </div>
      </header>
      <main className="container" style={{ flex: 1, paddingTop: '2rem', paddingBottom: '2rem' }}>
        <Outlet />
      </main>
      <footer style={{ background: 'var(--color-surface)', borderTop: '1px solid var(--color-border)', padding: '1.5rem 0' }}>
        <div className="container text-center text-sm text-secondary">
          SkillProof - Verified Problem-Solving Marketplace
        </div>
      </footer>
    </div>
  );
}