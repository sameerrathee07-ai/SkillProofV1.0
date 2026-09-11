import React from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import Layout from "./components/Layout";
import Homepage from "./pages/Homepage";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import PitchSession from "./pages/PitchSession";
import PitchResults from "./pages/PitchResults";
import Settings from "./pages/Settings";

/**
 * Shown while the stored token is being validated against /auth/me. Without
 * this, a reload would bounce an authenticated user to /login for a frame.
 */
function AuthPending() {
  return (
    <div className="au-page">
      <div className="au-pending" role="status" aria-live="polite">
        <span className="au-spinner" aria-hidden="true" />
        <span>Checking your session…</span>
      </div>
    </div>
  );
}

function PublicOnly({ children }) {
  const { loading, isAuthenticated } = useAuth();
  if (loading) return <AuthPending />;
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
}

/**
 * Guards on verified auth state, not on the mere presence of a token in
 * storage — a made-up token string must not open the app.
 */
function ProtectedRoute({ children }) {
  const { loading, isAuthenticated } = useAuth();
  const location = useLocation();
  if (loading) return <AuthPending />;
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  }
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<PublicOnly><Homepage /></PublicOnly>} />
        <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
        <Route path="/signup" element={<PublicOnly><Signup /></PublicOnly>} />
        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="chat/:sessionId?" element={<PitchSession />} />
          <Route path="results/:sessionId?" element={<PitchResults />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
