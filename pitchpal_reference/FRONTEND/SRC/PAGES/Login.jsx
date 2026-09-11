import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { Icon } from "../components/Icons";
import GoogleButton, { googleConfigured } from "../components/GoogleButton";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loginWithGoogle } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => { document.body.classList.remove("theme-dashboard"); }, []);

  // Return the user to whatever they were trying to reach before the redirect.
  const next = location.state?.from || "/dashboard";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate(next, { replace: true });
    } catch (err) {
      setError(err.message || "Could not sign in. Check your email and password.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async (credential) => {
    setError("");
    setLoading(true);
    try {
      await loginWithGoogle(credential);
      navigate(next, { replace: true });
    } catch (err) {
      setError(err.message || "Google sign-in failed. Try your email and password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="au-page">
      <div className="au-shell">
        <div className="au-brand">
          <Icon name="logo" size={26} color="#0f0f0f" />
          <Link to="/" className="au-brand-name">PitchPal</Link>
        </div>

        <div className="au-card">
          <h1 className="au-title">Welcome back</h1>
          <p className="au-sub">Sign in to continue your pitch sessions.</p>

          {error && (
            <div className="au-alert" role="alert">
              <Icon name="alertCircle" size={16} />
              <span>{error}</span>
            </div>
          )}

          {googleConfigured && (
            <>
              <GoogleButton
                onCredential={handleGoogle}
                onError={() => setError("Could not load Google sign-in. Use your email and password.")}
                text="signin_with"
              />
              <div className="au-divider">or</div>
            </>
          )}

          <form className="au-form" onSubmit={handleSubmit} noValidate>
            <div className="au-field">
              <label htmlFor="email" className="au-label">Email</label>
              <input
                id="email" type="email" className="au-input"
                value={email} onChange={(e) => setEmail(e.target.value)}
                placeholder="founder@startup.com" autoComplete="email"
                required disabled={loading}
              />
            </div>
            <div className="au-field">
              <label htmlFor="password" className="au-label">Password</label>
              <input
                id="password" type="password" className="au-input"
                value={password} onChange={(e) => setPassword(e.target.value)}
                placeholder="Your password" autoComplete="current-password"
                required disabled={loading}
              />
            </div>
            <button type="submit" className="au-submit" disabled={loading}>
              {loading ? <><span className="au-spinner" aria-hidden="true" /> Signing in…</> : "Sign in"}
            </button>
          </form>

          <p className="au-foot">
            New to PitchPal? <Link to="/signup">Create an account</Link>
          </p>
        </div>

        <p className="au-legal">
          By continuing you agree to our <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.
        </p>
      </div>
    </div>
  );
}
