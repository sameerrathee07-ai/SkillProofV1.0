import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import PostProblem from './pages/PostProblem';
import BrowseProblems from './pages/BrowseProblems';
import ProblemDetail from './pages/ProblemDetail';
import PitchChat from './pages/PitchChat';
import PitchResults from './pages/PitchResults';
import PosterInbox from './pages/PosterInbox';
import Tokens from './pages/Tokens';

function PrivateRoute({ children, allowedRoles }: { children: React.ReactNode; allowedRoles?: ('poster' | 'solver')[] }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="container" style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="text-secondary">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="container" style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="text-secondary">Loading...</div>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/signup" element={<PublicRoute><Signup /></PublicRoute>} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="problems/post" element={<PrivateRoute allowedRoles={['poster']}><PostProblem /></PrivateRoute>} />
        <Route path="problems" element={<BrowseProblems />} />
        <Route path="problems/:id" element={<ProblemDetail />} />
        <Route path="pitch/:sessionId" element={<PrivateRoute allowedRoles={['solver']}><PitchChat /></PrivateRoute>} />
        <Route path="pitch/:sessionId/results" element={<PrivateRoute allowedRoles={['solver']}><PitchResults /></PrivateRoute>} />
        <Route path="inbox" element={<PrivateRoute allowedRoles={['poster']}><PosterInbox /></PrivateRoute>} />
        <Route path="tokens" element={<PrivateRoute allowedRoles={['solver']}><Tokens /></PrivateRoute>} />
      </Route>
    </Routes>
  );
}

export default App;