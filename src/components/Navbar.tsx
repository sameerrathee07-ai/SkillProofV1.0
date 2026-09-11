import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth-context';
import { LogOut, PlusCircle, Search, LayoutDashboard, FileText, Settings } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="sticky top-0 z-50 bg-ivory/90 backdrop-blur-md border-b border-ink/10 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-ink font-serif text-2xl font-bold tracking-tight">
            <span className="w-8 h-8 rounded-md bg-ink text-ivory flex items-center justify-center font-sans font-extrabold text-lg shadow-sm">
              S<span className="text-brass">P</span>
            </span>
            <span>Skill<span className="text-brass">Proof</span></span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-6 text-sm font-medium">
            {isAuthenticated ? (
              user?.role === 'poster' ? (
                <>
                  <Link to="/dashboard" className="flex items-center gap-1.5 text-ink hover:text-brass transition-colors">
                    <LayoutDashboard className="w-4 h-4 text-brass" />
                    <span>My Listings</span>
                  </Link>
                  <Link to="/post-problem" className="flex items-center gap-1.5 text-ink hover:text-brass transition-colors">
                    <PlusCircle className="w-4 h-4 text-brass" />
                    <span>Post a Problem</span>
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/problems" className="flex items-center gap-1.5 text-ink hover:text-brass transition-colors">
                    <Search className="w-4 h-4 text-brass" />
                    <span>Browse Problems</span>
                  </Link>
                  <Link to="/my-proposals" className="flex items-center gap-1.5 text-ink hover:text-brass transition-colors">
                    <FileText className="w-4 h-4 text-brass" />
                    <span>My Proposals</span>
                  </Link>
                </>
              )
            ) : (
              <Link to="/problems" className="flex items-center gap-1.5 text-ink hover:text-brass transition-colors">
                <Search className="w-4 h-4 text-brass" />
                <span>Browse Problems</span>
              </Link>
            )}

            <Link to="/admin/seed" className="text-ink-muted hover:text-ink text-xs flex items-center gap-1 transition-colors">
              <Settings className="w-3.5 h-3.5" />
              <span>Demo Seed</span>
            </Link>
          </div>

          {/* User Auth CTAs */}
          <div className="flex items-center gap-3">
            {isAuthenticated && user ? (
              <div className="flex items-center gap-3">
                <div className="hidden sm:flex flex-col text-right">
                  <span className="text-sm font-semibold text-ink leading-tight">{user.fullName}</span>
                  <span className="text-xs uppercase tracking-wider font-semibold text-brass">
                    {user.role === 'poster' ? 'Problem Poster' : 'Solver'}
                  </span>
                </div>
                {user.role === 'solver' && (
                  <Link to={`/solver/${user.id}`} className="text-xs bg-forest-light text-forest font-semibold px-2.5 py-1 rounded-full border border-forest/20 hover:bg-forest/10 transition-colors">
                    Profile
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="p-2 text-ink-muted hover:text-brick hover:bg-brick-light rounded-md transition-colors"
                  title="Sign Out"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-medium text-ink hover:text-brass transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/signup"
                  className="px-4 py-2 text-sm font-medium bg-brass text-ink rounded-md hover:bg-brass-hover transition-colors shadow-sm font-semibold"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

        </div>
      </div>
    </nav>
  );
};
