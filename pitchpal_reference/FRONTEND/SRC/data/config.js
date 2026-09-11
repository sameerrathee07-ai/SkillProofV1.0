// ============================================================
// PitchPal — static app config and derivation helpers.
//
// This file holds no seed data. Users, sessions, scores, balances
// and usage all come from the backend. What lives here is the
// presentation contract that mirrors the server's own constants:
// the 6 scoring dimensions and the 5-step flow.
// ============================================================

/** The 6 scoring dimensions, keyed to match ScoreResponse on the backend. */
export const DIMENSIONS = [
  { key: "problem_clarity", label: "Problem Clarity" },
  { key: "market_specificity", label: "Market Specificity" },
  { key: "revenue_viability", label: "Revenue Viability" },
  { key: "competitive_awareness", label: "Competitive Awareness" },
  { key: "team_credibility", label: "Team Credibility" },
  { key: "investor_readiness", label: "Investor Readiness" },
];

/**
 * The 5-step flow. Labels, hints and placeholders are presentation only —
 * the authoritative question text arrives in each coach reply, and the
 * server decides what passes.
 */
export const STEPS = [
  {
    id: 1,
    name: "Idea",
    hint: "At least 10 words and a clear action verb.",
    placeholder: "We help X do Y by...",
  },
  {
    id: 2,
    name: "Customer",
    hint: "Include an age or number reference and a pain keyword.",
    placeholder: "Students aged 18-24 who struggle to...",
  },
  {
    id: 3,
    name: "Business Model",
    hint: "Include a price or currency and a frequency word (monthly, per user).",
    placeholder: "We charge Rs 499 per user, monthly...",
  },
  {
    id: 4,
    name: "Competition",
    hint: "Two competitor names and a differentiation phrase.",
    placeholder: "Unlike Acme and Globex, we...",
  },
  {
    id: 5,
    name: "Team",
    hint: "An experience claim and an advantage claim.",
    placeholder: "We spent 5 years at... our edge is...",
  },
];

export const TOTAL_STEPS = STEPS.length;

/** Tokens the server charges per chat message. Display only — never enforced here. */
export const TOKEN_COST_PER_MESSAGE = 2;

/** A full pitch is every step answered once. Mirrors payments.TOKENS_PER_PITCH. */
export const TOKENS_PER_PITCH = TOKEN_COST_PER_MESSAGE * TOTAL_STEPS;

/** Balance at or below which the token badge turns red. */
export const LOW_BALANCE_THRESHOLD = 10;

export const CURRENCY = "₹";

export const STATUS = {
  IN_PROGRESS: "In Progress",
  COMPLETED: "Completed",
  DRAFT: "Draft",
};

// Package names, token counts and prices all come from GET /tokens/packages.

// ---- Derivations from backend session rows ----

/**
 * Roll the session list into the dashboard's headline counters.
 *
 * This is the pitch counter: `total` is how many pitches this account has
 * created, so it reads 0 on a new account and lands on +1 as soon as the server
 * confirms another /session/start. Counting rows rather than keeping a running
 * tally means the number cannot drift from what the server actually stored.
 *
 * `bestScore` is null — not 0 — when nothing has been scored yet, so the card
 * can say so instead of implying a score of zero.
 */
export function pitchCounters(sessions) {
  const rows = Array.isArray(sessions) ? sessions : [];
  const scores = rows.map((s) => overallScore(parseScores(s))).filter((n) => n !== null);
  return {
    total: rows.length,
    completed: rows.filter((s) => s.completed).length,
    inProgress: rows.filter((s) => !s.completed).length,
    bestScore: scores.length ? Math.max(...scores) : null,
  };
}

/** How many full pitches a balance still covers. */
export function pitchesAffordable(balance) {
  const tokens = Number(balance) || 0;
  return Math.max(0, Math.floor(tokens / TOKENS_PER_PITCH));
}

/** A session is a Draft until the founder has answered anything. */
export function sessionStatus(session) {
  if (session.completed) return STATUS.COMPLETED;
  if ((session.current_step ?? 1) <= 1 && !session.pitch_text) return STATUS.DRAFT;
  return STATUS.IN_PROGRESS;
}

/**
 * Sessions have no title column. The step-1 answer *is* the one-line idea,
 * so use it as the card title and fall back for empty drafts.
 */
export function sessionTitle(session, maxLength = 42) {
  const first = (session.pitch_text || "")
    .split("\n")
    .map((line) => line.replace(/^\[\d+\]\s*/, "").trim())
    .find(Boolean);

  if (!first) return "Untitled pitch";
  if (first.length <= maxLength) return first;
  // Trim on a word boundary so titles don't end mid-word. A single word longer
  // than maxLength has no space to break on, so fall back to a hard cut.
  const breakAt = first.lastIndexOf(" ", maxLength);
  return first.slice(0, breakAt > 0 ? breakAt : maxLength).trimEnd() + "...";
}

export function parseScores(session) {
  if (!session?.scores_json) return null;
  try {
    return JSON.parse(session.scores_json);
  } catch {
    return null;
  }
}

/** The 6 dimensions average to a 0-100 headline score. */
export function overallScore(scores) {
  if (!scores) return null;
  const values = DIMENSIONS.map((d) => Number(scores[d.key])).filter((n) => Number.isFinite(n));
  if (!values.length) return null;
  return Math.round((values.reduce((a, b) => a + b, 0) / values.length) * 10);
}

export function dimsToArray(scores) {
  return DIMENSIONS.map((d) => ({ ...d, value: Number(scores?.[d.key]) || 0 }));
}

/** The lowest-scoring dimension — the one the Results page tags as "Focus". */
export function weakestDimension(scores) {
  if (!scores) return null;
  return dimsToArray(scores).reduce((low, d) => (d.value < low.value ? d : low));
}

/** "2 hours ago" / "Yesterday" / "3 days ago" from an ISO timestamp. */
export function relativeTime(iso) {
  if (!iso) return "";
  // Backend sends naive UTC; mark it as UTC so it isn't read as local time.
  const stamp = /[Z+]|-\d{2}:\d{2}$/.test(iso) ? iso : `${iso}Z`;
  const then = new Date(stamp);
  if (Number.isNaN(then.getTime())) return "";

  const seconds = Math.max(0, (Date.now() - then.getTime()) / 1000);
  if (seconds < 90) return "Just now";

  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;

  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;

  const days = Math.round(hours / 24);
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days} days ago`;

  const weeks = Math.round(days / 7);
  if (weeks < 5) return `${weeks} week${weeks === 1 ? "" : "s"} ago`;
  return then.toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

/** Initials for the avatar, from a Google name when present, else the email. */
export function initialsFor(user) {
  if (!user) return "";
  const source = (user.name || "").trim();
  if (source) {
    const parts = source.split(/\s+/);
    return ((parts[0]?.[0] || "") + (parts.length > 1 ? parts[parts.length - 1][0] : "")).toUpperCase();
  }
  return (user.email || "?").slice(0, 2).toUpperCase();
}

/** Display name for the avatar menu, derived rather than invented. */
export function displayName(user) {
  if (!user) return "";
  return user.name?.trim() || (user.email || "").split("@")[0];
}
