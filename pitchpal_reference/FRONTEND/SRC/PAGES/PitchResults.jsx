import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Icon } from "../components/Icons";
import RadarChart from "../components/RadarChart";
import { api } from "../lib/api";
import { useApi } from "../hooks/useApi";
import {
  DIMENSIONS,
  dimsToArray,
  overallScore,
  parseScores,
  relativeTime,
  sessionTitle,
  weakestDimension,
} from "../data/config";

const OUTLINE_SECTIONS = [
  { key: "problem", title: "Problem" },
  { key: "solution", title: "Solution" },
  { key: "customer", title: "Target Customer" },
  { key: "business_model", title: "Business Model" },
  { key: "competition", title: "Competition & Edge" },
  { key: "team", title: "Team & Advantage" },
  { key: "ask", title: "The Ask" },
];

export default function PitchResults() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  // With no id in the URL, fall back to the newest completed session.
  const resolve = useCallback(async () => {
    if (sessionId) return api.sessions.get(Number(sessionId));
    const history = await api.sessions.history();
    const newestCompleted = (history || []).find((s) => s.completed);
    if (!newestCompleted) return null;
    return api.sessions.get(newestCompleted.id);
  }, [sessionId]);

  const { data: session, loading, error, setData } = useApi(resolve, [sessionId]);

  const scores = useMemo(() => parseScores(session), [session]);
  const [scoring, setScoring] = useState(false);
  const [scoreError, setScoreError] = useState("");

  // A finished pitch that was never scored: ask the server to score it now.
  // Scores are computed and stored server-side; nothing is derived here.
  useEffect(() => {
    if (!session?.completed || scores || scoring) return;
    let cancelled = false;
    setScoring(true);
    api.sessions
      .score(session.id)
      .then((result) => {
        if (!cancelled) setData({ ...session, scores_json: JSON.stringify(result) });
      })
      .catch((err) => {
        if (!cancelled) setScoreError(err.message || "Could not score this pitch.");
      })
      .finally(() => { if (!cancelled) setScoring(false); });
    return () => { cancelled = true; };
  }, [session, scores, scoring, setData]);

  const outlineReq = useApi(
    () => (session?.completed ? api.sessions.outline(session.id) : null),
    [session?.id, session?.completed]
  );

  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState("");

  const downloadPdf = async () => {
    if (!session) return;
    setDownloading(true);
    setDownloadError("");
    try {
      const blob = await api.pdf.generate(session.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `pitchpal-${session.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setDownloadError(err.message || "Could not generate the PDF.");
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="pr-wrap">
        <div className="ps-loading" role="status" aria-live="polite">
          <span className="au-spinner" aria-hidden="true" />
          <span>Loading your results…</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pr-wrap">
        <div className="db-empty">
          <div className="db-empty-icon"><Icon name="alertCircle" size={24} /></div>
          <h3>Could not load these results</h3>
          <p>{error.message}</p>
          <button className="db-cta-new" onClick={() => navigate("/dashboard")}>Back to dashboard</button>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="pr-wrap">
        <div className="db-empty">
          <div className="db-empty-icon"><Icon name="trophy" size={24} /></div>
          <h3>No scored pitches yet</h3>
          <p>Finish all five steps of a pitch and its six-dimension breakdown appears here.</p>
          <button className="db-cta-new" onClick={() => navigate("/chat")}>
            <Icon name="plus" size={16} /> Start a pitch
          </button>
        </div>
      </div>
    );
  }

  if (!session.completed) {
    const step = Math.min(session.current_step ?? 1, DIMENSIONS.length);
    return (
      <div className="pr-wrap">
        <div className="db-empty">
          <div className="db-empty-icon"><Icon name="target" size={24} /></div>
          <h3>This pitch is not finished</h3>
          <p>You are on step {step} of 5. Scores unlock once all five steps pass.</p>
          <button className="db-cta-new" onClick={() => navigate(`/chat/${session.id}`)}>
            Continue this pitch <Icon name="arrowRight" size={15} />
          </button>
        </div>
      </div>
    );
  }

  if (scoring && !scores) {
    return (
      <div className="pr-wrap">
        <div className="ps-loading" role="status" aria-live="polite">
          <span className="au-spinner" aria-hidden="true" />
          <span>Scoring your pitch…</span>
        </div>
      </div>
    );
  }

  if (!scores) {
    return (
      <div className="pr-wrap">
        <div className="db-empty">
          <div className="db-empty-icon"><Icon name="alertCircle" size={24} /></div>
          <h3>Scores are not available</h3>
          <p>{scoreError || "This pitch has not been scored yet."}</p>
          <button className="db-cta-new" onClick={() => navigate("/dashboard")}>Back to dashboard</button>
        </div>
      </div>
    );
  }

  const dims = dimsToArray(scores);
  const dimValues = Object.fromEntries(dims.map((d) => [d.key, d.value]));
  const weakest = weakestDimension(scores);
  const overall = overallScore(scores);
  const outline = outlineReq.data;

  return (
    <div className="pr-wrap">
      <div className="pr-head">
        <div>
          <h1 className="pr-title">{sessionTitle(session, 60)}</h1>
          <p className="pr-sub">
            Scored across six investor dimensions · started {relativeTime(session.started_at)}
          </p>
        </div>
        <div className="pr-overall">
          <b>{overall}</b>
          <span>/ 100 overall</span>
        </div>
      </div>

      <div className="pr-top">
        <div className="pr-radar-card">
          <div className="pr-card-title">Six-dimension radar</div>
          <RadarChart dims={dimValues} />
        </div>

        <div className="pr-scores-card" id="scores">
          <div className="pr-card-title">Score breakdown</div>
          <div className="pr-score-list">
            {dims.map((d) => {
              const isFocus = d.key === weakest?.key;
              return (
                <div key={d.key} className="pr-score-item">
                  <div className="pr-score-row">
                    <span className="pr-score-name">
                      {d.label}
                      {isFocus && <span className="pr-focus-tag">Focus</span>}
                    </span>
                    <span className="pr-score-val">{d.value}/10</span>
                  </div>
                  <div className="pr-score-track">
                    <div
                      className={`pr-score-fill ${isFocus ? "warm" : ""}`}
                      style={{ width: `${d.value * 10}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {scores.feedback && (
        <div className="pr-feedback">
          <div className="pr-feedback-label">Where to focus next</div>
          <p>{scores.feedback}</p>
        </div>
      )}

      <div className="pr-card-title" style={{ maxWidth: 1000, margin: "0 auto 16px" }}>Pitch outline</div>
      {outlineReq.loading ? (
        <div className="pr-sections" aria-hidden="true">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="pr-section-card">
              <div className="db-skeleton db-skeleton-title" />
              <div className="db-skeleton db-skeleton-line" />
            </div>
          ))}
        </div>
      ) : outlineReq.error ? (
        <p className="db-panel-empty" style={{ maxWidth: 1000, margin: "0 auto 24px" }}>
          Could not load the outline. {outlineReq.error.message}
        </p>
      ) : (
        <div className="pr-sections">
          {OUTLINE_SECTIONS.filter((s) => outline?.[s.key]).map((s) => (
            <div key={s.key} className="pr-section-card">
              <div className="pr-section-title">{s.title}</div>
              <p className="pr-section-body">{outline[s.key]}</p>
            </div>
          ))}
        </div>
      )}

      <div className="pr-actions">
        {downloadError && (
          <div className="au-alert" role="alert">
            <Icon name="alertCircle" size={16} />
            <span>{downloadError}</span>
          </div>
        )}
        <button className="btn btn-primary-dark pr-download" onClick={downloadPdf} disabled={downloading}>
          {downloading ? (
            <><span className="au-spinner" aria-hidden="true" /> Preparing PDF…</>
          ) : (
            <><Icon name="download" size={17} /> Download PDF Pitch Deck</>
          )}
        </button>
      </div>
    </div>
  );
}
