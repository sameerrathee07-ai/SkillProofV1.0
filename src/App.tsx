import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/auth-context';
import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';

const HeroLanding = React.lazy(() => import('./pages/HeroLanding').then(m => ({ default: m.HeroLanding })));
const SignupPage = React.lazy(() => import('./pages/SignupPage').then(m => ({ default: m.SignupPage })));
const LoginPage = React.lazy(() => import('./pages/LoginPage').then(m => ({ default: m.LoginPage })));
const PostProblemForm = React.lazy(() => import('./pages/PostProblemForm').then(m => ({ default: m.PostProblemForm })));
const BrowseProblems = React.lazy(() => import('./pages/BrowseProblems').then(m => ({ default: m.BrowseProblems })));
const PitchGatePage = React.lazy(() => import('./pages/PitchGatePage').then(m => ({ default: m.PitchGatePage })));
const ProposalDetail = React.lazy(() => import('./pages/ProposalDetail').then(m => ({ default: m.ProposalDetail })));
const SolverProfile = React.lazy(() => import('./pages/SolverProfile').then(m => ({ default: m.SolverProfile })));
const SolverDashboard = React.lazy(() => import('./pages/SolverDashboard').then(m => ({ default: m.SolverDashboard })));
const PosterDashboard = React.lazy(() => import('./pages/PosterDashboard').then(m => ({ default: m.PosterDashboard })));
const AdminSeed = React.lazy(() => import('./pages/AdminSeed').then(m => ({ default: m.AdminSeed })));
const PrivacyPolicy = React.lazy(() => import('./pages/PrivacyPolicy').then(m => ({ default: m.PrivacyPolicy })));
const TermsOfService = React.lazy(() => import('./pages/TermsOfService').then(m => ({ default: m.TermsOfService })));

const PageLoader = () => (
  <div className="min-h-[60vh] flex items-center justify-center text-ink-muted">
    <div className="flex items-center gap-3 text-sm font-medium">
      <div className="w-5 h-5 border-2 border-brass border-t-transparent rounded-full animate-spin" />
      <span>Loading...</span>
    </div>
  </div>
);

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route element={<Layout />}>
              
              {/* Public Routes */}
              <Route path="/" element={<HeroLanding />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/privacy" element={<PrivacyPolicy />} />
              <Route path="/terms" element={<TermsOfService />} />
              <Route path="/solver/:solverId" element={<SolverProfile />} />
              <Route path="/admin/seed" element={<AdminSeed />} />

              {/* Poster Protected Routes */}
              <Route element={<ProtectedRoute requiredRole="poster" />}>
                <Route path="/post-problem" element={<PostProblemForm />} />
                <Route path="/dashboard" element={<PosterDashboard />} />
              </Route>

              {/* Solver Protected Routes */}
              <Route element={<ProtectedRoute requiredRole="solver" />}>
                <Route path="/problems" element={<BrowseProblems />} />
                <Route path="/pitch/:problemId" element={<PitchGatePage />} />
                <Route path="/my-proposals" element={<SolverDashboard />} />
              </Route>

              {/* Proposal Detail (Poster/Solver authenticated) */}
              <Route element={<ProtectedRoute />}>
                <Route path="/proposals/:proposalId" element={<ProposalDetail />} />
              </Route>

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />

            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
