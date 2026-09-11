# SkillProof

**A verified problem-solving marketplace for tertiary-sector businesses — built around a mandatory pitch-quality gate that filters out low-effort proposals before they ever reach a problem-poster's inbox.**

---

## The Problem

Businesses, shops, and schools in tertiary sectors have real operational problems but no fast, low-cost way to source solutions. Posting to a generic freelance platform produces a flood of vague, copy-pasted responses, forcing the problem-owner to manually sift through noise before any real evaluation can happen.

At the same time, students and early-career solvers who could genuinely help have no structured way to demonstrate they've understood the problem before pitching — so serious responses get buried in the same pile as low-effort ones.

The core gap isn't a missing marketplace — it's a missing **quality gate**. Nothing on either side currently requires a solver to prove they understand the problem, the customer, the business case, and their own credibility before their pitch reaches a problem-owner.

## Target Users

| Segment | Role | Need |
|---|---|---|
| Companies, shops, schools | Problem-poster | Post a real operational problem and receive only vetted, high-quality proposals |
| College students, early solvers | Solver | A credible way to pitch a solution and be taken seriously against a pool of low-effort competitors |

## How It Works

**Problem-posters** sign up, describe their problem, and set a budget and timeline. Their listing goes live and they receive only proposals that have already cleared the quality gate — ranked and ready to review.

**Solvers** browse open problems and pitch a solution through **PitchPal**, a guided, five-step pitch conversation. Each pitch is scored automatically across six dimensions of quality. Only pitches that clear the bar are released to the problem-poster; pitches that fall short stay private, with the solver shown exactly where to improve and a chance to revise and resubmit.

This gate is the product's core mechanic: it replaces manual filtering with an automated, transparent bar that every solver must clear before being seen.

## Key Features

- **Guided pitch flow** — a structured, step-by-step chat walks solvers through articulating their idea, customer, business case, competitive edge, and credibility.
- **Automated quality scoring** — every pitch is scored across six dimensions (clarity, market fit, revenue viability, competitive awareness, credibility, investor readiness) with no manual review required.
- **Actionable feedback loop** — pitches that don't clear the bar get specific, targeted feedback instead of a flat rejection, and can be revised and resubmitted.
- **Solver credibility profiles** — a running score built from a solver's pitch history, shown to problem-posters alongside each proposal.
- **Proposal export** — each submitted proposal is compiled into a shareable document for the problem-poster.
- **Resumable sessions** — solvers can leave mid-pitch and pick up exactly where they left off.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Backend | FastAPI + SQLAlchemy |
| Database | SQLite |
| Authentication | JWT-based session auth |
| Scoring engine | Rule-based (no external AI API) |
| Document export | ReportLab |
| Deployment | Vercel (frontend) + Render (backend) |

## Project Status

Currently a prototype, validated at demo scale. The pitch-quality threshold and a few scoring edge cases (e.g. problems with no direct "competitors," such as internal school workflows) are still being tuned. Payment integration, multi-language support, and real-time negotiation between parties are intentionally out of scope for this stage.

---

*SkillProof is built to prove that a good idea, well-pitched, deserves to be seen — and a weak pitch deserves the chance to get better before it's judged.*
