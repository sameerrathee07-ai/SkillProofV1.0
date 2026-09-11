import React from "react";
import { STATUS, TOTAL_STEPS } from "../data/config";

// Status pill — maps a session status string to its badge style.
export function StatusBadge({ status }) {
  const cls =
    status === STATUS.COMPLETED
      ? "badge-completed"
      : status === STATUS.IN_PROGRESS
      ? "badge-in-progress"
      : "badge-draft";
  return <span className={`badge ${cls}`}>{status}</span>;
}

// 5-dot step progress indicator.
export function StepDots({ step, total = TOTAL_STEPS }) {
  return (
    <div className="db-dots" aria-hidden="true">
      {Array.from({ length: total }, (_, i) => (
        <span key={i} className={`db-dot ${i < step ? "filled" : ""}`} />
      ))}
    </div>
  );
}
