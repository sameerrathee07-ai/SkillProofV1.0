import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/auth-context';
import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';

import { HeroLanding } from './pages/HeroLanding';
import { SignupPage } from './pages/SignupPage';
import { LoginPage } from './pages/LoginPage';
import { PostProblemForm } from './pages/PostProblemForm';
import { BrowseProblems } from './pages/BrowseProblems';
import { PitchGatePage } from './pages/PitchGatePage';
import { ProposalDetail } from './pages/ProposalDetail';
import { SolverProfile } from './pages/SolverProfile';
import { SolverDashboard } from './pages/SolverDashboard';
import { PosterDashboard } from './pages/PosterDashboard';
import { AdminSeed } from './pages/AdminSeed';

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            
            {/* Public Routes */}
            <Route path="/" element={<HeroLanding />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/login" element={<LoginPage />} />
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
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
