import React from "react";
import { useNavigate, useOutletContext } from "react-router-dom";
import { Icon } from "../components/Icons";
import { useAuth } from "../hooks/useAuth";
import { displayName } from "../data/config";

export default function Settings() {
  const navigate = useNavigate();
  const { openTokens } = useOutletContext() || {};
  const { user, tokenBalance, signOut, loading } = useAuth();

  const handleSignOut = () => {
    signOut();
    navigate("/", { replace: true });
  };

  const signedInWith = user?.picture || user?.name ? "Google" : "Email and password";

  return (
    <div className="st-wrap">
      <div className="st-card">
        <h3>Account</h3>
        {loading && !user ? (
          <>
            <div className="db-skeleton db-skeleton-line" />
            <div className="db-skeleton db-skeleton-line" />
          </>
        ) : (
          <>
            <div className="st-field">
              <span className="st-label">Name</span>
              <div className="st-value">{displayName(user) || "Not set"}</div>
            </div>
            <div className="st-field">
              <span className="st-label">Email</span>
              <div className="st-value">{user?.email || "—"}</div>
            </div>
            <div className="st-field">
              <span className="st-label">Sign-in method</span>
              <div className="st-value">{signedInWith}</div>
            </div>
          </>
        )}
      </div>

      <div className="st-card">
        <h3>Tokens</h3>
        <div className="st-field">
          <span className="st-label">Current balance</span>
          <div className="st-value">
            <b style={{ fontFamily: "var(--font-display)", color: "var(--db-accent-warm)" }}>
              {loading && !user ? "—" : tokenBalance}
            </b> tokens
          </div>
        </div>
        <p className="st-value" style={{ color: "var(--db-text-muted)", fontSize: 13, marginBottom: 16 }}>
          Balance is managed by the server. The frontend never changes it.
        </p>
        <button className="btn btn-primary" onClick={() => openTokens?.()}>
          <Icon name="wallet" size={15} /> Buy tokens
        </button>
      </div>

      <div className="st-card">
        <h3>Session</h3>
        <button className="btn btn-ghost" onClick={handleSignOut}>
          <Icon name="logout" size={15} /> Log out
        </button>
      </div>
    </div>
  );
}
