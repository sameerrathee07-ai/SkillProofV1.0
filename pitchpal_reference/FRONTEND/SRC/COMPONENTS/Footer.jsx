import React from "react";
import { Link } from "react-router-dom";

// Minimal editorial footer — appears on every page.
export default function Footer() {
  const noop = (e) => e.preventDefault();
  return (
    <footer className="pp-footer" role="contentinfo">
      <div className="pp-footer-inner">
        <div className="pp-footer-brand">
          <Link to="/" className="pp-footer-logo">PitchPal</Link>
          <span className="pp-footer-copy">© 2025</span>
        </div>
        <nav className="pp-footer-links" aria-label="Legal">
          <a href="#" onClick={noop}>Terms of Service</a>
          <a href="#" onClick={noop}>Privacy Policy</a>
        </nav>
      </div>
    </footer>
  );
}
