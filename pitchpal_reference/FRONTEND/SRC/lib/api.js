// Single gateway to the FastAPI backend.
// The base URL is build-time configurable so a deployed frontend can point at a
// real host; it falls back to the local dev server.
const API_BASE = (import.meta.env.VITE_API_BASE || "http://localhost:8000/api").replace(/\/+$/, "");

const TOKEN_KEY = "pitchpal_token";
const USER_KEY = "pitchpal_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setSession(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/** Raised on a 402 so callers can show the top-up prompt instead of a generic error. */
export class OutOfTokensError extends Error {
  constructor(message) {
    super(message || "Out of tokens");
    this.name = "OutOfTokensError";
  }
}

/**
 * Events fired after a write the server accepted, so any mounted view showing a
 * derived count can re-read it. They carry no numbers: the count still comes
 * from the server, this only says "now would be a good time to ask".
 */
export const EVENT_PITCH_CREATED = "pitchpal:pitch-created";
export const EVENT_PDF_DOWNLOADED = "pitchpal:pdf-downloaded";

function authHeaders() {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function handleResponse(res) {
  if (res.ok) return res.status === 204 ? null : res.json();

  // A rejected token is never valid again — drop it so the route guards stop
  // treating this browser as signed in.
  if (res.status === 401) {
    clearSession();
    window.dispatchEvent(new Event("pitchpal:unauthorized"));
  }

  const body = await res.json().catch(() => null);
  const detail = body?.detail;
  const message = typeof detail === "string" ? detail : `Request failed (${res.status})`;

  if (res.status === 402) throw new OutOfTokensError(message);
  throw new Error(message);
}

const get = (path) => fetch(`${API_BASE}${path}`, { headers: authHeaders() }).then(handleResponse);

const post = (path, body) =>
  fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: authHeaders(),
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  }).then(handleResponse);

export const api = {
  auth: {
    signup: (email, password) => post("/auth/signup", { email, password }),
    login: (email, password) => post("/auth/login", { email, password }),
    /** Exchange a Google Identity Services ID token for our own JWT. */
    google: (credential) => post("/auth/google", { credential }),
    me: () => get("/auth/me"),
  },

  sessions: {
    start: async () => {
      const started = await post("/session/start");
      // The pitch count just went up by one. Announce it so the dashboard's
      // counter advances even if it stayed mounted behind the chat.
      window.dispatchEvent(new Event(EVENT_PITCH_CREATED));
      return started;
    },
    chat: (sessionId, content) => post("/session/chat", { session_id: sessionId, content }),
    score: (sessionId) => post("/session/score", { session_id: sessionId }),
    history: () => get("/session/history"),
    get: (sessionId) => get(`/session/${sessionId}`),
    outline: (sessionId) => get(`/session/${sessionId}/outline`),
  },

  pdf: {
    /** Resolves to a Blob, not JSON — handled separately from the helpers above. */
    generate: async (sessionId) => {
      const res = await fetch(`${API_BASE}/pdf/generate`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ session_id: sessionId }),
      });
      if (!res.ok) {
        if (res.status === 401) {
          clearSession();
          window.dispatchEvent(new Event("pitchpal:unauthorized"));
        }
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail || "Could not generate the PDF");
      }
      // The server counted this export; tell the dashboard to re-read it.
      window.dispatchEvent(new Event(EVENT_PDF_DOWNLOADED));
      return res.blob();
    },
  },

  tokens: {
    balance: () => get("/tokens/balance"),
    /** The one-time packs, flat shape, for the marketing pricing grid. */
    packages: () => get("/tokens/packages"),
    /** Public: every plan, payment method and live promo, priced in one currency. */
    catalog: (currency) =>
      get(`/tokens/catalog${currency ? `?currency=${encodeURIComponent(currency)}` : ""}`),
    /**
     * Price one plan for this account, with any promo code applied.
     * The server owns every number here — the client renders, it never subtracts.
     */
    quote: (plan, { currency, promoCode } = {}) =>
      post("/tokens/quote", {
        plan,
        currency: currency || null,
        promo_code: promoCode || null,
      }),
    usage: () => get("/tokens/usage"),
    purchase: (packageName) => post("/tokens/purchase", { package: packageName }),
  },
};
