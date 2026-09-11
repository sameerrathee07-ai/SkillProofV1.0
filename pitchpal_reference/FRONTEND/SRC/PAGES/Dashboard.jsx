import React, { useEffect, useMemo } from "react";
import { useNavigate, useOutletContext, Link } from "react-router-dom";
import { Icon } from "../components/Icons";
import MetricCards from "../components/MetricCards";
import { StatusBadge, StepDots } from "../components/Bits";
import { api, EVENT_PDF_DOWNLOADED, EVENT_PITCH_CREATED } from "../lib/api";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../hooks/useAuth";
import {
  STATUS,
  TOTAL_STEPS,
  overallScore,
  parseScores,
  pitchCounters,
  relativeTime,
  sessionStatus,
  sessionTitle,
} from "../data/config";

function SessionCard({ session, onContinue, onView }) {
  const status = sessionStatus(session);
  const completed = status === STATUS.COMPLETED;
  const score = overallScore(parseScores(session));
  const step = Math.min(session.current_step ?? 1, TOTAL_STEPS);

  return (
    <article className="db-session-card">
      <div className="db-session-head">
        <div>
          <h3 className="db-session-title">{sessionTitle(session)}</h3>
          <div className="db-session-meta">Started {relativeTime(session.started_at)}</div>
        </div>
        <StatusBadge status={status} />
      </div>

      {completed ? (
        <div className="db-session-score">
          {score === null ? (
            <span className="db-step-label">Not scored yet</span>
          ) : (
            <>
              <b>{score}</b>
              <span>/ 100</span>
            </>
          )}
        </div>
      ) : (
        <div className="db-session-progress">
          <span className="db-step-label">Step {step} of {TOTAL_STEPS}</span>
          <StepDots step={step} />
        </div>
      )}

      <div className="db-session-foot">
        {completed ? (
          <>
            <button className="btn btn-ghost" onClick={() => onView(session.id)}>
              <Icon name="eye" size={15} /> View Results
            </button>
            <button className="btn btn-primary" onClick={() => onView(session.id)}>
              <Icon name="refresh" size={15} /> Revisit
            </button>
          </>
        ) : (
          <button className="btn btn-primary btn-block" onClick={() => onContinue(session.id)}>
            Continue <Icon name="arrowRight" size={15} />
          </button>
        )}
      </div>
    </article>
  );
}

function SessionSkeleton() {
  return (
    <article className="db-session-card" aria-hidden="true">
      <div className="db-skeleton db-skeleton-title" />
      <div className="db-skeleton db-skeleton-line" />
      <div className="db-skeleton db-skeleton-block" />
    </article>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { search = "" } = useOutletContext() || {};
  const { user, tokenBalance, pdfDownloads, loading: authLoading } = useAuth();

  const sessionsReq = useApi(() => api.sessions.history(), []);
  const usageReq = useApi(() => api.tokens.usage(), []);

  const allSessions = sessionsReq.data || [];
  const usage = usageReq.data || [];

  // Starting a pitch elsewhere in the app advances the counter here. Re-reading
  // the history is what makes it +1 — the count is never incremented locally,
  // so it always matches the rows the server kept.
  useEffect(() => {
    const onPitchCreated = () => sessionsReq.reload();
    window.addEventListener(EVENT_PITCH_CREATED, onPitchCreated);
    window.addEventListener(EVENT_PDF_DOWNLOADED, onPitchCreated);
    return () => {
      window.removeEventListener(EVENT_PITCH_CREATED, onPitchCreated);
      window.removeEventListener(EVENT_PDF_DOWNLOADED, onPitchCreated);
    };
  }, [sessionsReq.reload]);

  const q = search.trim().toLowerCase();
  const sessions = useMemo(
    () => (q ? allSessions.filter((s) => sessionTitle(s, 200).toLowerCase().includes(q)) : allSessions),
    [allSessions, q]
  );

  // Every metric is derived from what the server returned. Nothing is seeded, so
  // a brand-new account reads 0 pitches rather than a placeholder.
  const counters = useMemo(() => pitchCounters(allSessions), [allSessions]);
  const metrics = useMemo(
    () => ({
      tokenBalance,
      pitches: counters.total,
      bestScore: counters.bestScore,
      pdfDownloads,
    }),
    [counters, tokenBalance, pdfDownloads]
  );

  // Per-card, so the balance appears with the profile instead of waiting on the
  // unrelated session-history request.
  const metricsLoading = {
    tokenBalance: authLoading && !user,
    pitches: sessionsReq.loading,
    bestScore: sessionsReq.loading,
    pdfDownloads: (authLoading && !user) || sessionsReq.loading,
  };

  // Most recent unfinished pitch — the one worth resuming.
  const resumable = useMemo(
    () => allSessions.find((s) => !s.completed) || null,
    [allSessions]
  );

  const maxUsage = Math.max(1, ...usage.map((d) => d.tokens));
  const totalUsage = usage.reduce((sum, d) => sum + d.tokens, 0);

  return (
    <>
      {/* ROW 1 — metrics */}
      <section className="db-row">
        <MetricCards metrics={metrics} loading={metricsLoading} />
      </section>

      {/* ROW 2 — heading + CTA */}
      <section className="db-row">
        <div className="db-section-head">
          <h2 className="db-section-title">Your Pitches</h2>
          <button className="db-cta-new" onClick={() => navigate("/chat")}>
            <Icon name="plus" size={16} /> Start New Pitch
          </button>
        </div>

        {/* ROW 3 — session grid, with real loading / error / empty branches */}
        {sessionsReq.loading ? (
          <div className="db-sessions">
            <SessionSkeleton /><SessionSkeleton /><SessionSkeleton />
          </div>
        ) : sessionsReq.error ? (
          <div className="db-empty">
            <div className="db-empty-icon"><Icon name="alertCircle" size={24} /></div>
            <h3>Could not load your pitches</h3>
            <p>{sessionsReq.error.message}</p>
            <button className="db-cta-new" onClick={sessionsReq.reload}>
              <Icon name="refresh" size={16} /> Try again
            </button>
          </div>
        ) : sessions.length === 0 ? (
          <div className="db-empty">
            <div className="db-empty-icon"><Icon name={q ? "search" : "messageSquare"} size={24} /></div>
            <h3>{q ? "No pitches found" : "No pitches yet"}</h3>
            <p>
              {q
                ? `Nothing matches “${search}”. Try another title.`
                : "Start your first pitch and it will show up here."}
            </p>
            {!q && (
              <button className="db-cta-new" onClick={() => navigate("/chat")}>
                <Icon name="plus" size={16} /> Start New Pitch
              </button>
            )}
          </div>
        ) : (
          <div className="db-sessions">
            {sessions.map((s) => (
              <SessionCard
                key={s.id}
                session={s}
                onContinue={(id) => navigate(`/chat/${id}`)}
                onView={(id) => navigate(`/results/${id}`)}
              />
            ))}
          </div>
        )}
      </section>

      {/* ROW 4 — resume prompt + token usage */}
      <section className="db-row4">
        <div className="db-panel">
          <div className="db-section-head" style={{ marginBottom: 0 }}>
            <h3 className="db-panel-title" style={{ marginBottom: 0 }}>Recent activity</h3>
            {resumable && (
              <Link
                to={`/chat/${resumable.id}`}
                className="db-step-label"
                style={{ color: "var(--db-accent)" }}
              >
                Resume {sessionTitle(resumable, 24)} →
              </Link>
            )}
          </div>

          {sessionsReq.loading ? (
            <div className="db-snippet" style={{ marginTop: 16 }} aria-hidden="true">
              <div className="db-skeleton db-skeleton-line" />
              <div className="db-skeleton db-skeleton-line" />
            </div>
          ) : resumable ? (
            <div className="db-snippet" style={{ marginTop: 16 }}>
              <div className="db-snippet-row coach">
                <span className="db-snippet-role">Coach</span>
                <span className="db-snippet-text">
                  You are on step {Math.min(resumable.current_step ?? 1, TOTAL_STEPS)} of {TOTAL_STEPS}.
                  Pick up where you left off.
                </span>
              </div>
              <div className="db-snippet-row coach">
                <span className="db-snippet-role">Started</span>
                <span className="db-snippet-text">{relativeTime(resumable.started_at)}</span>
              </div>
            </div>
          ) : (
            <p className="db-panel-empty" style={{ marginTop: 16 }}>
              No pitch in progress. Every session you finish shows its score above.
            </p>
          )}
        </div>

        <div className="db-panel">
          <h3 className="db-panel-title">Token usage · last 7 days</h3>
          {usageReq.loading ? (
            <div className="db-skeleton db-skeleton-block" aria-hidden="true" />
          ) : usageReq.error ? (
            <p className="db-panel-empty">Could not load usage.</p>
          ) : (
            <>
              <div className="db-bars">
                {usage.map((d) => (
                  <div key={d.date} className="db-bar-col">
                    <div className="db-bar-track">
                      <div
                        className={`db-bar-fill ${d.tokens > 0 && d.tokens === maxUsage ? "warm" : ""}`}
                        style={{ height: `${(d.tokens / maxUsage) * 100}%` }}
                        title={`${d.tokens} tokens`}
                      />
                    </div>
                    <span className="db-bar-label">{d.day}</span>
                  </div>
                ))}
              </div>
              <div className="db-usage-total">
                <b>{totalUsage}</b> tokens spent this week
              </div>
            </>
          )}
        </div>
      </section>
    </>
  );
}
