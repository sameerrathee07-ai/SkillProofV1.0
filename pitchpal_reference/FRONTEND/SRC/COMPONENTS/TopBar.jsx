import React from "react";
import { useLocation } from "react-router-dom";
import { Icon } from "./Icons";
import { useAuth } from "../hooks/useAuth";
import { LOW_BALANCE_THRESHOLD, displayName, initialsFor } from "../data/config";

const TITLES = [
  [/^\/dashboard/, "Dashboard"],
  [/^\/chat/, "Pitch Session"],
  [/^\/results/, "Pitch Results"],
  [/^\/settings/, "Settings"],
];

function titleFor(pathname) {
  const match = TITLES.find(([re]) => re.test(pathname));
  return match ? match[1] : "PitchPal";
}

export default function TopBar({ onOpenMenu, onOpenTokens, search, onSearch }) {
  const { pathname } = useLocation();
  const { user, tokenBalance, loading } = useAuth();

  // Only call a balance "low" once it's actually known — a still-loading 0
  // would otherwise flash the red warning state on every page load.
  const known = !loading && !!user;
  const low = known && tokenBalance < LOW_BALANCE_THRESHOLD;

  return (
    <header className="db-topbar">
      <button className="db-menu-btn" onClick={onOpenMenu} aria-label="Open menu">
        <Icon name="menu" size={22} />
      </button>
      <h1 className="db-page-title">{titleFor(pathname)}</h1>

      <div className="db-topbar-spacer" />

      <div className="db-search">
        <Icon name="search" size={16} />
        <input
          type="search"
          placeholder="Search pitches"
          value={search ?? ""}
          onChange={(e) => onSearch?.(e.target.value)}
          aria-label="Search pitches"
        />
      </div>

      <button
        type="button"
        className={`db-token-badge ${low ? "low" : ""}`}
        onClick={onOpenTokens}
        aria-label={known ? `${tokenBalance} tokens. Buy more.` : "Loading token balance"}
        title="Buy tokens"
      >
        <Icon name={low ? "alertCircle" : "coin"} size={15} />
        {known ? tokenBalance : "—"}
      </button>

      <div className="db-avatar" title={displayName(user)}>
        {user?.picture ? (
          <img src={user.picture} alt="" referrerPolicy="no-referrer" />
        ) : (
          initialsFor(user)
        )}
      </div>
    </header>
  );
}
