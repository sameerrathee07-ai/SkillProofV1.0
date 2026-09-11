import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { Icon } from "../components/Icons";
import GoogleButton, { googleConfigured } from "../components/GoogleButton";

const BENEFITS = [
  "20 free tokens on signup",
  "Full 5-step pitch validation",
  "Six-dimension scoring and PDF export",
  "Resumable sessions",
];

export default function Signup() {
  const navigate = useNavigate();
  const { signup, loginWithGoogle } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => { document.body.classList.remove("theme-dashboard"); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (password !== confirm) return setError("Passwords do not match.");
    if (password.length < 8) return setError("Password must be at least 8 characters.");
    setLoading(true);
    try {
      await signup(email, password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || "Could not create your account. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async (credential) => {
    setError("");
    setLoading(true);
    try {
      await loginWithGoogle(credential);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || "Google sign-up failed. Try creating an account with email.");
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
          <h1 className="au-title">Create your account</h1>
          <p className="au-sub">Start with 20 free tokens. No credit card required.</p>

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
                onError={() => setError("Could not load Google sign-in. Create an account with email instead.")}
                text="signup_with"
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
                placeholder="At least 8 characters" autoComplete="new-password"
                required minLength={8} disabled={loading}
              />
              <span className="au-hint">At least 8 characters.</span>
            </div>
            <div className="au-field">
              <label htmlFor="confirm" className="au-label">Confirm password</label>
              <input
                id="confirm" type="password" className="au-input"
                value={confirm} onChange={(e) => setConfirm(e.target.value)}
                placeholder="Re-enter your password" autoComplete="new-password"
                required disabled={loading}
              />
            </div>
            <button type="submit" className="au-submit" disabled={loading}>
              {loading ? <><span className="au-spinner" aria-hidden="true" /> Creating account…</> : "Create account"}
            </button>
          </form>

          <div className="au-benefits">
            <div className="au-benefits-title">What you get</div>
            <ul>
              {BENEFITS.map((b) => (
                <li key={b}><Icon name="check" size={14} /> {b}</li>
              ))}
            </ul>
          </div>

          <p className="au-foot">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>

        <p className="au-legal">
          By continuing you agree to our <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.
        </p>
      </div>
    </div>
  );
}
