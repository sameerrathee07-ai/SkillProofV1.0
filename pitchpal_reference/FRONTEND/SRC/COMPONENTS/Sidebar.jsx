import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Icon } from "./Icons";
import { useAuth } from "../hooks/useAuth";

// Nav model. `type: "link"` routes; `type: "action"` fires a handler (modal / logout).
const SECTIONS = [
  {
    label: "Workspace",
    items: [
      { type: "link", to: "/dashboard", label: "Dashboard", icon: "home" },
      { type: "link", to: "/chat", label: "New Pitch", icon: "plus" },
    ],
  },
  {
    label: "Analytics",
    items: [
      { type: "link", to: "/results", label: "Pitch Results", icon: "fileText" },
      { type: "link", to: "/results#scores", label: "Scores", icon: "target" },
    ],
  },
  {
    label: "Account",
    items: [
      { type: "action", action: "tokens", label: "Token Packages", icon: "wallet" },
      { type: "link", to: "/settings", label: "Settings", icon: "settings" },
      { type: "action", action: "logout", label: "Log out", icon: "logout", danger: true },
    ],
  },
];

export default function Sidebar({ open, onOpenTokens, onNavigate }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { signOut } = useAuth();
  const current = location.pathname + (location.hash || "");

  const isActive = (to) => {
    if (to.includes("#")) return current === to;
    // plain path: active on exact match, but not when a hash variant is showing
    return location.pathname === to && !location.hash;
  };

  const handleAction = (action) => {
    if (action === "tokens") onOpenTokens?.();
    if (action === "logout") {
      // Go through the auth context so React state clears too — wiping
      // localStorage alone would leave the app rendered as signed in.
      signOut();
      navigate("/", { replace: true });
    }
    onNavigate?.();
  };

  return (
    <aside className={`db-sidebar ${open ? "open" : ""}`} aria-label="Main navigation">
      <div className="db-sidebar-brand">
        <Icon name="logo" size={26} color="#3b6e45" />
        <Link to="/dashboard" className="db-sidebar-logo">PitchPal</Link>
      </div>

      <nav className="db-sidebar-nav">
        {SECTIONS.map((section) => (
          <div key={section.label} className="db-nav-section">
            <div className="db-nav-label">{section.label}</div>
            {section.items.map((item) =>
              item.type === "link" ? (
                <Link
                  key={item.label}
                  to={item.to}
                  className={`db-nav-item ${isActive(item.to) ? "active" : ""}`}
                  onClick={onNavigate}
                  aria-current={isActive(item.to) ? "page" : undefined}
                >
                  <Icon name={item.icon} size={18} />
                  <span>{item.label}</span>
                </Link>
              ) : (
                <button
                  key={item.label}
                  type="button"
                  className={`db-nav-item ${item.danger ? "danger" : ""}`}
                  onClick={() => handleAction(item.action)}
                >
                  <Icon name={item.icon} size={18} />
                  <span>{item.label}</span>
                </button>
              )
            )}
          </div>
        ))}
      </nav>
    </aside>
  );
}
