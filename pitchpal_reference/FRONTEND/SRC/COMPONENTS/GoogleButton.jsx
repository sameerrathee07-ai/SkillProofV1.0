import React, { useEffect, useRef, useState } from "react";

const GOOGLE_CLIENT_ID = (import.meta.env.VITE_GOOGLE_CLIENT_ID || "").trim();
const GSI_SRC = "https://accounts.google.com/gsi/client";

export const googleConfigured = Boolean(GOOGLE_CLIENT_ID);

/** Load the Google Identity Services script once, shared across mounts. */
let gsiPromise = null;
function loadGsi() {
  if (gsiPromise) return gsiPromise;

  gsiPromise = new Promise((resolve, reject) => {
    if (window.google?.accounts?.id) return resolve(window.google);

    const existing = document.querySelector(`script[src="${GSI_SRC}"]`);
    const script = existing || Object.assign(document.createElement("script"), {
      src: GSI_SRC,
      async: true,
      defer: true,
    });

    script.addEventListener("load", () => resolve(window.google));
    script.addEventListener("error", () => reject(new Error("Could not reach Google")));
    if (!existing) document.head.appendChild(script);
  });

  return gsiPromise;
}

/**
 * Renders Google's own sign-in button.
 *
 * The button hands back an ID token, which we forward untouched to the backend.
 * The browser is never trusted to assert who the user is — the server verifies
 * the token's signature and audience before issuing a session.
 *
 * Renders nothing when VITE_GOOGLE_CLIENT_ID is unset, so the form still works
 * on a machine without Google credentials configured.
 */
export default function GoogleButton({ onCredential, onError, text = "signin_with" }) {
  const holder = useRef(null);
  const [failed, setFailed] = useState(false);

  // Keep the newest callbacks reachable without re-initialising the button.
  const cbRef = useRef({ onCredential, onError });
  useEffect(() => { cbRef.current = { onCredential, onError }; }, [onCredential, onError]);

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return;
    let cancelled = false;

    loadGsi()
      .then((google) => {
        if (cancelled || !holder.current) return;
        google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: ({ credential }) => {
            if (credential) cbRef.current.onCredential?.(credential);
          },
          // Keeps the credential exchange bound to this origin.
          ux_mode: "popup",
        });
        google.accounts.id.renderButton(holder.current, {
          type: "standard",
          theme: "outline",
          size: "large",
          text,
          shape: "pill",
          logo_alignment: "center",
          width: 340,
        });
      })
      .catch((err) => {
        if (cancelled) return;
        setFailed(true);
        cbRef.current.onError?.(err);
      });

    return () => { cancelled = true; };
  }, [text]);

  if (!GOOGLE_CLIENT_ID) return null;

  return (
    <div className="au-google">
      <div ref={holder} className="au-google-btn" />
      {failed && (
        <p className="au-google-fallback">
          Google sign-in is unavailable right now. Use your email and password below.
        </p>
      )}
    </div>
  );
}
