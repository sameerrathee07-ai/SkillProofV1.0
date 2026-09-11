import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, clearSession, getToken, setSession, EVENT_PDF_DOWNLOADED } from "../lib/api";

const AuthContext = createContext(null);

/**
 * Holds the signed-in user for the whole app.
 *
 * The server is the only source of truth for identity and token balance: on
 * mount we validate whatever token is in storage against /auth/me and sign out
 * if it's rejected. Nothing here ever writes a balance.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState(getToken() ? "loading" : "signed-out");

  const signOut = useCallback(() => {
    clearSession();
    setUser(null);
    setStatus("signed-out");
  }, []);

  // Adopt a fresh JWT: store it, then confirm it by reading the profile back.
  const adopt = useCallback(async (accessToken) => {
    setSession(accessToken);
    const profile = await api.auth.me();
    setUser(profile);
    setStatus("signed-in");
    return profile;
  }, []);

  const refresh = useCallback(async () => {
    if (!getToken()) {
      setUser(null);
      setStatus("signed-out");
      return null;
    }
    try {
      const profile = await api.auth.me();
      setUser(profile);
      setStatus("signed-in");
      return profile;
    } catch (err) {
      // A rejected token means signed out. A network failure does not — keep the
      // session and let the next call retry rather than logging the user out
      // because the backend blipped.
      if (!getToken()) {
        setUser(null);
        setStatus("signed-out");
      } else {
        setStatus("error");
      }
      throw err;
    }
  }, []);

  useEffect(() => {
    if (!getToken()) return;
    refresh().catch(() => {});
  }, [refresh]);

  // api.js fires this when any request comes back 401.
  useEffect(() => {
    const onUnauthorized = () => {
      setUser(null);
      setStatus("signed-out");
    };
    window.addEventListener("pitchpal:unauthorized", onUnauthorized);
    return () => window.removeEventListener("pitchpal:unauthorized", onUnauthorized);
  }, []);

  // A finished PDF export bumps a server-side counter. Re-read the profile so
  // the dashboard's "decks generated" reflects it without a page reload.
  useEffect(() => {
    const onDownloaded = () => {
      if (getToken()) refresh().catch(() => {});
    };
    window.addEventListener(EVENT_PDF_DOWNLOADED, onDownloaded);
    return () => window.removeEventListener(EVENT_PDF_DOWNLOADED, onDownloaded);
  }, [refresh]);

  const login = useCallback(
    async (email, password) => adopt((await api.auth.login(email, password)).access_token),
    [adopt]
  );

  const signup = useCallback(
    async (email, password) => adopt((await api.auth.signup(email, password)).access_token),
    [adopt]
  );

  const loginWithGoogle = useCallback(
    async (credential) => adopt((await api.auth.google(credential)).access_token),
    [adopt]
  );

  /**
   * Record a balance the server just reported (e.g. the remaining_tokens in a
   * /chat response) so the header updates without another round trip.
   *
   * This mirrors a server-computed value — it never derives or adjusts one. The
   * frontend has no say in what a message costs.
   */
  const applyServerBalance = useCallback((balance) => {
    if (typeof balance !== "number") return;
    setUser((prev) => (prev ? { ...prev, token_balance: balance } : prev));
  }, []);

  const value = useMemo(
    () => ({
      user,
      status,
      loading: status === "loading",
      isAuthenticated: status === "signed-in",
      tokenBalance: user?.token_balance ?? 0,
      /** Decks exported, counted server-side on each successful /pdf/generate. */
      pdfDownloads: user?.pdf_downloads ?? 0,
      login,
      signup,
      loginWithGoogle,
      signOut,
      refresh,
      // Same round trip as refresh(), named for the callers that only care about
      // the balance. Re-reading the profile is the only way to learn a balance;
      // there is no client-side path that could adjust one.
      refreshBalance: refresh,
      applyServerBalance,
    }),
    [user, status, login, signup, loginWithGoogle, signOut, refresh, applyServerBalance]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
