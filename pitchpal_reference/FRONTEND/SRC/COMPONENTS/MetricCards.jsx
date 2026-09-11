import React from "react";
import { Icon } from "./Icons";
import { TOKEN_COST_PER_MESSAGE, pitchesAffordable } from "../data/config";

/**
 * The four headline metrics.
 *
 * Each card owns its own empty wording, because "nothing yet" and "zero" are
 * different facts: a founder with no pitches has no best score, they do not
 * have a best score of 0. Cards render a placeholder string in that case, and
 * the /100 suffix is suppressed so it never reads "No pitches/100".
 */
const CARDS = [
  {
    key: "tokenBalance",
    label: "Token Balance",
    icon: "coin",
    gold: true,
    value: (m) => m.tokenBalance ?? 0,
    sub: (m) => {
      const balance = m.tokenBalance ?? 0;
      if (balance <= 0) return "Out of tokens — top up to keep going";
      const pitches = pitchesAffordable(balance);
      if (pitches < 1) return `Under one full pitch · ${TOKEN_COST_PER_MESSAGE} per answer`;
      return `Enough for ${pitches} full ${pitches === 1 ? "pitch" : "pitches"}`;
    },
  },
  {
    key: "pitches",
    label: "Pitches",
    icon: "messageSquare",
    value: (m) => m.pitches ?? 0,
    sub: (m) => (m.pitches ? "Total created" : "None created yet"),
  },
  {
    key: "bestScore",
    label: "Best Score",
    icon: "trophy",
    suffix: "/100",
    // No pitches at all, versus pitches that exist but are not finished — the
    // founder can act on the second one, so say which it is.
    value: (m) => {
      if (!m.pitches) return "No pitches";
      if (m.bestScore === null || m.bestScore === undefined) return "Not scored yet";
      return m.bestScore;
    },
    sub: (m) => (m.pitches ? "Across completed pitches" : "Finish a pitch to get scored"),
  },
  {
    key: "pdfDownloads",
    label: "PDF Downloads",
    icon: "download",
    value: (m) => (m.pitches ? m.pdfDownloads ?? 0 : "No pitches"),
    sub: (m) => (m.pitches ? "Decks generated" : "Complete a pitch to export one"),
  },
];

export default function MetricCards({ metrics, loading = false }) {
  // `loading` is either one flag for every card or a per-key map, so the token
  // balance can render the moment the profile lands instead of waiting on the
  // unrelated session-history request.
  const isLoading = (key) => (typeof loading === "object" && loading !== null ? !!loading[key] : !!loading);

  return (
    <div className="db-metrics">
      {CARDS.map((c) => {
        const shown = c.value(metrics || {});
        const isPlaceholder = typeof shown === "string";
        return (
          <div key={c.key} className="db-metric-card">
            <div className="db-metric-top">
              <span className="db-metric-label">{c.label}</span>
              <span className="db-metric-icon"><Icon name={c.icon} size={16} /></span>
            </div>
            {isLoading(c.key) ? (
              <div className="db-skeleton db-skeleton-value" aria-hidden="true" />
            ) : (
              <div
                className={`db-metric-value ${c.gold && !isPlaceholder ? "gold" : ""} ${
                  isPlaceholder ? "db-metric-empty" : ""
                }`}
              >
                {shown}
                {c.suffix && !isPlaceholder && <span className="db-metric-suffix">{c.suffix}</span>}
              </div>
            )}
            <div className="db-metric-sub">{c.sub(metrics || {})}</div>
          </div>
        );
      })}
    </div>
  );
}
