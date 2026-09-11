import React, { useState, useRef, useEffect, useCallback } from "react";
import { useParams, useNavigate, useOutletContext } from "react-router-dom";
import { Icon } from "../components/Icons";
import { api, OutOfTokensError } from "../lib/api";
import { useAuth } from "../hooks/useAuth";
import { STEPS, TOTAL_STEPS, TOKEN_COST_PER_MESSAGE } from "../data/config";

/**
 * The 5-step pitch session.
 *
 * All validation and all token accounting happen on the server. This page sends
 * the answer, renders the coach's reply, and infers pass/fail only from whether
 * the server advanced current_step. There is no client-side rule engine — a copy
 * of the rules here could disagree with the server and would be trivial to edit.
 */
export default function PitchSession() {
  const { sessionId: routeId } = useParams();
  const navigate = useNavigate();
  const { openTokens } = useOutletContext() || {};
  const { applyServerBalance, tokenBalance } = useAuth();

  const [sessionId, setSessionId] = useState(routeId ? Number(routeId) : null);
  const [step, setStep] = useState(1);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [done, setDone] = useState(false);
  const [booting, setBooting] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [outOfTokens, setOutOfTokens] = useState(false);
  const [spent, setSpent] = useState(0);

  const chatEndRef = useRef(null);
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  /**
   * Which session this component has already opened. A ref, because it has to
   * gate the effect *before* the first await: POST /session/start is not
   * idempotent, so a second invocation (React StrictMode in development, or any
   * remount) would create a second empty session and orphan it.
   */
  const bootedRef = useRef(null);

  // Resume an existing session, or open a new one. Runs once per route id.
  useEffect(() => {
    const target = routeId ? Number(routeId) : "new";
    if (bootedRef.current === target) return;
    bootedRef.current = target;

    (async () => {
      setBooting(true);
      setError("");
      try {
        if (routeId) {
          const session = await api.sessions.get(Number(routeId));
          setSessionId(session.id);
          setStep(Math.min(session.current_step ?? 1, TOTAL_STEPS));
          setDone(Boolean(session.completed));
          setMessages(
            (session.messages || []).map((m) => ({
              role: m.role === "user" ? "user" : "coach",
              text: m.content,
              pass: null, // history doesn't record verdicts; don't invent them
            }))
          );
        } else {
          const started = await api.sessions.start();
          // Claim the id before navigating, so the re-run this navigation
          // triggers recognises the session as already open.
          bootedRef.current = started.session_id;
          setSessionId(started.session_id);
          setStep(started.current_step ?? 1);
          setMessages([{ role: "coach", text: started.message, pass: null }]);
          // Put the id in the URL so a refresh resumes instead of starting over.
          navigate(`/chat/${started.session_id}`, { replace: true });
        }
      } catch (err) {
        bootedRef.current = null; // let a retry through
        setError(err.message || "Could not open this pitch session.");
      } finally {
        setBooting(false);
      }
    })();
  }, [routeId, navigate]);

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || sending || done || !sessionId) return;

    setSending(true);
    setError("");
    const stepBefore = step;

    // Show the answer immediately; the verdict fills in from the response.
    setMessages((prev) => [...prev, { role: "user", text, pass: null }]);
    setInput("");

    try {
      const res = await api.sessions.chat(sessionId, text);

      // The server advancing the step is what "passed" means.
      const advanced = res.pitch_complete || res.current_step > stepBefore;

      setMessages((prev) => {
        const next = [...prev];
        for (let i = next.length - 1; i >= 0; i--) {
          if (next[i].role === "user") { next[i] = { ...next[i], pass: advanced }; break; }
        }
        next.push({ role: "coach", text: res.reply, pass: advanced ? null : false });
        return next;
      });

      setStep(Math.min(res.current_step ?? stepBefore, TOTAL_STEPS));
      setSpent((n) => n + TOKEN_COST_PER_MESSAGE);
      applyServerBalance(res.remaining_tokens);
      if (res.pitch_complete) setDone(true);
    } catch (err) {
      // Roll the optimistic bubble back out; the answer was not recorded.
      setMessages((prev) => {
        const idx = prev.map((m) => m.role).lastIndexOf("user");
        return idx === -1 ? prev : prev.filter((_, i) => i !== idx);
      });
      setInput(text);
      if (err instanceof OutOfTokensError) {
        setOutOfTokens(true);
      } else {
        setError(err.message || "Could not send that answer. Try again.");
      }
    } finally {
      setSending(false);
    }
  }, [input, sending, done, sessionId, step, applyServerBalance]);

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const currentStep = STEPS[Math.min(step, TOTAL_STEPS) - 1] || STEPS[0];

  if (booting) {
    return (
      <div className="ps-wrap">
        <div className="ps-loading" role="status" aria-live="polite">
          <span className="au-spinner" aria-hidden="true" />
          <span>Opening your pitch session…</span>
        </div>
      </div>
    );
  }

  if (error && !messages.length) {
    return (
      <div className="ps-wrap">
        <div className="db-empty">
          <div className="db-empty-icon"><Icon name="alertCircle" size={24} /></div>
          <h3>Could not open this session</h3>
          <p>{error}</p>
          <button className="db-cta-new" onClick={() => navigate("/dashboard")}>
            Back to dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ps-wrap">
      {/* 5-step progress */}
      <div className="ps-progress" aria-label={`Step ${step} of ${TOTAL_STEPS}`}>
        {STEPS.map((s, i) => {
          const state = i + 1 < step || done ? "done" : i + 1 === step ? "current" : "upcoming";
          return (
            <React.Fragment key={s.id}>
              <div className={`ps-pill ${state}`}>
                <span className="ps-pill-num">
                  {state === "done" ? <Icon name="check" size={13} /> : s.id}
                </span>
                <span className="ps-pill-name">{s.name}</span>
              </div>
              {i < STEPS.length - 1 && <span className="ps-pill-bar" />}
            </React.Fragment>
          );
        })}
      </div>

      {/* Current step. The authoritative question text is whatever the coach
          just asked in the chat below; this card carries the label and the rule. */}
      {!done && (
        <div className="ps-stepcard">
          <div className="ps-step-eyebrow">Step {step} of {TOTAL_STEPS}</div>
          <div className="ps-step-q">{currentStep.name}</div>
          <div className="ps-step-hint">{currentStep.hint}</div>
        </div>
      )}

      {/* chat */}
      <div className="ps-chat">
        {messages.map((m, i) => (
          <div key={i} className={`ps-msg ${m.role}`}>
            <span className="ps-msg-label">{m.role === "coach" ? "Coach" : "You"}</span>
            <div className={`ps-bubble ${m.pass === false ? "fail" : m.pass === true ? "pass" : ""}`}>
              {m.text}
            </div>
          </div>
        ))}
        {sending && (
          <div className="ps-msg coach">
            <span className="ps-msg-label">Coach</span>
            <div className="ps-bubble ps-bubble-thinking" aria-live="polite">Checking your answer…</div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {outOfTokens && (
        <div className="ps-outoftokens" role="alert">
          <div>
            <h3>You are out of tokens</h3>
            <p>Each answer costs {TOKEN_COST_PER_MESSAGE} tokens. Top up to finish this pitch.</p>
          </div>
          <button className="btn btn-primary-dark" onClick={() => openTokens?.()}>
            <Icon name="wallet" size={15} /> View packages
          </button>
        </div>
      )}

      {done ? (
        <div className="ps-done">
          <div>
            <h3>Pitch complete</h3>
            <p>All five steps passed. Your scored breakdown is ready.</p>
          </div>
          <button className="btn btn-primary-dark" onClick={() => navigate(`/results/${sessionId}`)}>
            View Results <Icon name="arrowRight" size={15} />
          </button>
        </div>
      ) : (
        <>
          {error && (
            <div className="au-alert" role="alert">
              <Icon name="alertCircle" size={16} />
              <span>{error}</span>
            </div>
          )}
          <div className="ps-statusrow">
            <span className="ps-saved"><Icon name="check" size={13} /> Session saved</span>
            <span className="ps-cost">
              {spent > 0 && <>{spent} tokens used this session · </>}
              {tokenBalance} left
            </span>
          </div>
          <div className="ps-inputbar">
            <textarea
              className="ps-input"
              placeholder={currentStep.placeholder}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              rows={1}
              disabled={sending || outOfTokens}
              aria-label={`Your answer for step ${step}`}
            />
            <div className="ps-send-wrap">
              <button
                className="ps-send"
                onClick={handleSend}
                disabled={!input.trim() || sending || outOfTokens}
                aria-label="Send answer"
              >
                <Icon name="send" size={18} />
              </button>
              <span className="ps-cost">−{TOKEN_COST_PER_MESSAGE} tokens</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
