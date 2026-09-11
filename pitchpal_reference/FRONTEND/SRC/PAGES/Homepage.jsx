import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Icon } from "../components/Icons";
import Footer from "../components/Footer";
import { api } from "../lib/api";
import { useApi } from "../hooks/useApi";
import { CURRENCY } from "../data/config";

const HERO_POINTS = [
  "Build a structured pitch in 5 steps",
  "Get scored across 6 investor dimensions",
  "Download a PDF deck instantly",
];

const PROCESS = [
  { n: "01", name: "Idea", desc: "One sentence on what you do, in plain language." },
  { n: "02", name: "Customer", desc: "Who it is for and the exact pain you remove." },
  { n: "03", name: "Business Model", desc: "What you charge, who pays, how often." },
  { n: "04", name: "Competition", desc: "Two rivals and why a customer picks you." },
  { n: "05", name: "Team", desc: "Your experience and your unfair advantage." },
];

const SCORE_PREVIEW = [
  ["Problem Clarity", 8],
  ["Market Specificity", 7],
  ["Revenue Viability", 6],
  ["Competitive Awareness", 8],
  ["Team Credibility", 7],
  ["Investor Readiness", 8],
];

// Prices live on the server (GET /tokens/packages, public). Only the marketing
// line per package is copy, so that is all this file holds.
const PACKAGE_NOTES = {
  starter: "Enough for a full first pitch.",
  standard: "Best for iterating on two pitches.",
  pro: "For serial founders and heavy testing.",
  team: "One pool, shared across a founding team.",
};

// Compact 6-axis radar, blue fill — decorative preview only.
function RadarPreview() {
  const size = 150;
  const c = size / 2;
  const maxR = size * 0.4;
  const vals = [8, 7, 6, 8, 7, 8];
  const angle = (i) => (i / 6) * 2 * Math.PI - Math.PI / 2;
  const pt = (r, i) => [c + Math.cos(angle(i)) * r, c + Math.sin(angle(i)) * r];
  const ring = (level) =>
    [...Array(6)].map((_, i) => pt((level / 4) * maxR, i).join(",")).join(" ");
  const shape = vals.map((v, i) => pt((v / 10) * maxR, i).join(",")).join(" ");
  return (
    <svg viewBox={`0 0 ${size} ${size}`} width="100%" height="150" aria-hidden="true">
      {[1, 2, 3, 4].map((l) => (
        <polygon key={l} points={ring(l)} fill="none" stroke="#e5e7eb" strokeWidth="1" />
      ))}
      {vals.map((_, i) => {
        const [x, y] = pt(maxR, i);
        return <line key={i} x1={c} y1={c} x2={x} y2={y} stroke="#e5e7eb" strokeWidth="1" />;
      })}
      <polygon points={shape} fill="rgba(59,130,246,0.15)" stroke="#3b82f6" strokeWidth="2" />
      {vals.map((v, i) => {
        const [x, y] = pt((v / 10) * maxR, i);
        return <circle key={i} cx={x} cy={y} r="3" fill="#3b82f6" />;
      })}
    </svg>
  );
}

export default function Homepage() {
  const [audience, setAudience] = useState("students");
  const [scrolled, setScrolled] = useState(false);

  // Public endpoint — no sign-in needed to show what tokens cost.
  const packages = useApi(api.tokens.packages, []);

  useEffect(() => {
    document.body.classList.remove("theme-dashboard");
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="hp">
      {/* 1. TOP NAV */}
      <header className={`hp-nav ${scrolled ? "scrolled" : ""}`}>
        <div className="hp-container hp-nav-inner">
          <Link to="/" className="hp-logo">PitchPal</Link>
          <nav className="hp-nav-links" aria-label="Primary">
            <a href="#process">How it works</a>
            <a href="#results">Results</a>
            <a href="#pricing">Pricing</a>
          </nav>
          <div className="hp-nav-cta">
            <Link to="/login" className="hp-link-ghost">Log in</Link>
            <Link to="/signup" className="hp-pill-dark">Start free</Link>
          </div>
        </div>
      </header>

      {/* 2. HERO */}
      <section className="hp-hero hp-container">
        <div className="hp-hero-left">
          <div className="hp-toggle" role="group" aria-label="Audience">
            <button
              className={`hp-toggle-pill ${audience === "students" ? "active" : ""}`}
              onClick={() => setAudience("students")}
              aria-pressed={audience === "students"}
            >
              For Students
            </button>
            <button
              className={`hp-toggle-pill ${audience === "founders" ? "active" : ""}`}
              onClick={() => setAudience("founders")}
              aria-pressed={audience === "founders"}
            >
              For Founders
            </button>
          </div>

          <h1 className="hp-headline">
            Validate <span className="hp-accent">your pitch</span>
            <br />before the room
            <br />goes quiet.
          </h1>

          <ul className="hp-points">
            {HERO_POINTS.map((p) => (
              <li key={p}>
                <span className="hp-check"><Icon name="check" size={13} /></span>
                {p}
              </li>
            ))}
          </ul>

          <div className="hp-hero-cta">
            <Link to="/signup" className="hp-pill-dark hp-pill-lg">Start free — 20 tokens</Link>
            <a href="#process" className="hp-link-arrow">
              See how it works <Icon name="arrowRight" size={15} />
            </a>
          </div>
        </div>

        <div className="hp-hero-right">
          <div className="hp-hero-swatch">
            <div className="hp-mock-card">
              <div className="hp-mock-head">
                <div className="hp-mock-dot" />
                <span className="hp-mock-title">Pitch session</span>
                <span className="hp-mock-step">Step 2 / 5</span>
              </div>
              <div className="hp-mock-body">
                <div className="hp-bubble coach fail">
                  <span className="hp-bubble-label">Coach</span>
                  Too vague to advance. Add an age or situation and name the pain.
                </div>
                <div className="hp-bubble user">
                  Grades 9-12 teachers, 28-45, who waste 6+ hours a week hand-grading.
                </div>
                <div className="hp-bubble coach pass">
                  <span className="hp-bubble-label">Coach</span>
                  Strong. Advancing to Step 3 — Business Model.
                </div>
              </div>
            </div>
            <div className="hp-stat-strip">
              <span>5 steps</span><i>·</i><span>6 scores</span><i>·</i><span>1 PDF</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. HOW IT WORKS */}
      <section className="hp-section hp-container" id="process">
        <span className="hp-eyebrow">The process</span>
        <div className="hp-steps">
          <div className="hp-steps-line" aria-hidden="true" />
          {PROCESS.map((s) => (
            <div key={s.n} className="hp-step">
              <div className="hp-step-num">{s.n}</div>
              <div className="hp-step-name">{s.name}</div>
              <p className="hp-step-desc">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 4. WHAT YOU GET */}
      <section className="hp-getwrap" id="results">
        <div className="hp-container">
          <span className="hp-eyebrow">What you get</span>
          <div className="hp-get-grid">
            <article className="hp-get-card">
              <RadarPreview />
              <h3 className="hp-get-title">Six-dimension radar</h3>
              <p className="hp-get-sub">See strengths and gaps at a glance.</p>
            </article>

            <article className="hp-get-card">
              <div className="hp-score-list">
                {SCORE_PREVIEW.map(([label, val]) => (
                  <div key={label} className="hp-score-row">
                    <span className="hp-score-name">{label}</span>
                    <span className="hp-score-pill">{val}<i>/10</i></span>
                  </div>
                ))}
              </div>
              <h3 className="hp-get-title">Scored breakdown</h3>
              <p className="hp-get-sub">Every dimension, one to ten.</p>
            </article>

            <article className="hp-get-card">
              <div className="hp-pdf-thumb" aria-hidden="true">
                <div className="hp-pdf-title">Pitch Deck</div>
                <div className="hp-pdf-line w70" />
                <div className="hp-pdf-line w90" />
                <div className="hp-pdf-bars">
                  {[60, 80, 45, 70, 55, 75].map((h, i) => (
                    <span key={i} style={{ height: `${h}%` }} />
                  ))}
                </div>
              </div>
              <h3 className="hp-get-title">PDF pitch deck</h3>
              <p className="hp-get-sub">Dark-themed, ready to send.</p>
            </article>
          </div>
        </div>
      </section>

      {/* 5. PRICING / TOKENS */}
      <section className="hp-section hp-container" id="pricing">
        <span className="hp-eyebrow">Tokens</span>
        {packages.loading ? (
          <div className="hp-price-grid" aria-hidden="true">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="hp-price-card">
                <div className="db-skeleton db-skeleton-value" />
                <div className="db-skeleton db-skeleton-line" />
              </div>
            ))}
          </div>
        ) : packages.error || !packages.data?.length ? (
          <p className="hp-price-note">Pricing is unavailable right now.</p>
        ) : (
          <div className="hp-price-grid">
            {packages.data.map((p) => (
              <div key={p.id} className={`hp-price-card ${p.popular ? "featured" : ""}`}>
                <span className="hp-soon">Coming soon</span>
                <div className="hp-price-amount">{CURRENCY}{p.price_inr}</div>
                <div className="hp-price-tokens">{p.tokens} tokens</div>
                <p className="hp-price-note">{PACKAGE_NOTES[p.id] || `${p.tokens} coaching tokens.`}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <Footer />
    </div>
  );
}
