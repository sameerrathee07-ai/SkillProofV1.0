import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import { useAuth } from './hooks/useAuth'
import ProblemsPage from './pages/ProblemsPage'
import ProblemDetailPage from './pages/ProblemDetailPage'
import PostProblemPage from './pages/PostProblemPage'
import PitchPage from './pages/PitchPage'
import ResultsPage from './pages/ResultsPage'
import MyProposalsPage from './pages/MyProposalsPage'
import ProposalsPage from './pages/ProposalsPage'
import DashboardPage from './pages/DashboardPage'
import LoginPage, { SignupPage } from './pages/AuthPage'

function PrivateRoute({ children, allowedRoles }: { children: React.ReactNode; allowedRoles?: ('poster' | 'solver')[] }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="container">Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route element={<Layout />}> 
        <Route path="/" element={<PrivateRoute><ProblemsPage /></PrivateRoute>} />
        <Route path="/problems/:id" element={<PrivateRoute><ProblemDetailPage /></PrivateRoute>} />
        <Route path="/post-problem" element={<PrivateRoute allowedRoles={["poster"]}><PostProblemPage /></PrivateRoute>} />
        <Route path="/pitch/:id" element={<PrivateRoute allowedRoles={["solver"]}><PitchPage /></PrivateRoute>} />
        <Route path="/results/:id" element={<PrivateRoute allowedRoles={["solver"]}><ResultsPage /></PrivateRoute>} />
        <Route path="/my-proposals" element={<PrivateRoute allowedRoles={["solver"]}><MyProposalsPage /></PrivateRoute>} />
        <Route path="/proposals/:id" element={<PrivateRoute allowedRoles={["poster"]}><ProposalsPage /></PrivateRoute>} />
        <Route path="/dashboard" element={<PrivateRoute allowedRoles={["solver"]}><DashboardPage /></PrivateRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}