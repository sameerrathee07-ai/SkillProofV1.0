"""Authenticity fixture for the PitchPal rule engine.

The point is not "does a good pitch pass" — it is "can I predict the exact
scorecard before running it". The scorer is deterministic keyword heuristics, so
a hand-auditable pitch has exactly one correct output. If the six numbers come
back as predicted, scoring really ran. If they come back rounder, prettier or
just different, something is canned.

Run from BACKEND/:  py check_pitch_fixture.py
"""
import ai_service as ai

# ── The pitch under test ────────────────────────────────────────────────
STRONG = {
    1: "ClinicQueue cuts the expensive front-desk chaos at small clinics by "
       "automating patient check-in and flagging likely no-shows.",
    2: "Clinic managers aged 30 to 55 running 2 to 4 doctor practices waste 3 "
       "hours a day on phone reminders, and 20 percent of booked slots go "
       "empty, a problem that quietly eats their margin.",
    3: "We charge ₹1,200 per clinic monthly on a recurring subscription, "
       "and larger groups pay per seat.",
    4: "Practo and Zoho handle bookings, but unlike them we predict no-shows, "
       "which is our edge on retention.",
    5: "I led engineering at a hospital group for 6 years and shipped their "
       "scheduling stack; our unfair advantage is proprietary no-show data "
       "from 40 clinics.",
}

# Each near-miss removes exactly ONE required signal from a passing answer, so a
# rejection pins the blame on that single rule rather than on vagueness.
NEAR_MISSES = [
    (1, "ClinicQueue is a smart modern platform for small clinics everywhere today.",
     "10+ words but no action verb"),
    (1, "ClinicQueue cuts clinic chaos.", "action verb but under 10 words"),
    (2, "Clinic managers running small practices waste hours a day on reminders.",
     "pain word but no number"),
    (2, "Clinic managers aged 30 to 55 run 2 to 4 doctor practices every day.",
     "number but no pain word"),
    (3, "We charge ₹1,200 per clinic and larger groups pay more than that.",
     "price but no frequency"),
    (3, "Clinics pay us monthly on a recurring subscription for every seat.",
     "frequency but no price"),
    (4, "Practo handles bookings, but unlike them we predict no-shows.",
     "differentiation but only 1 competitor"),
    (4, "Practo and Zoho both handle clinic bookings for practices like these.",
     "2 competitors but no differentiation"),
    (5, "I led engineering at a hospital group for 6 years and shipped scheduling.",
     "experience but no unfair advantage"),
    (5, "Our unfair advantage is proprietary no-show data from 40 clinics.",
     "advantage but no experience claim"),
]

fails = []


def check(label, got, want=None):
    ok = got if want is None else got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {label} :: {got!r}")
    if not ok:
        fails.append(label)


print("== every step passes ==")
for step, answer in STRONG.items():
    r = ai.process_answer(step, answer)
    check(f"step {step} accepted", r.passed, True)

print("\n== near misses are rejected, one rule at a time ==")
for step, answer, why in NEAR_MISSES:
    r = ai.process_answer(step, answer)
    check(f"step {step} rejects: {why}", (r.passed, r.next_step), (False, step))

pitch_text = "\n".join(f"[{i}] {STRONG[i]}" for i in sorted(STRONG))
scores = ai.score_pitch(pitch_text)

print("\n== the scorecard, to be pinned as expected values ==")
DIMS = ["problem_clarity", "market_specificity", "revenue_viability",
        "competitive_awareness", "team_credibility", "investor_readiness"]
for d in DIMS:
    print(f"  {d:24} {scores[d]}")
print(f"  {'feedback':24} {scores['feedback']}")

vals = [scores[d] for d in DIMS]
overall = round(sum(vals) / len(vals) * 10)
print(f"\n  overall (frontend formula) {overall}/100")
print(f"  weakest dimension          {min(DIMS, key=lambda d: scores[d])}")

print("\n== the scorer discriminates ==")
weak_text = "[1] An app for clinics.\n[2] Everyone.\n[3] Free.\n[4] Nobody does this.\n[5] I just started."
weak = ai.score_pitch(weak_text)
weak_overall = round(sum(weak[d] for d in DIMS) / len(DIMS) * 10)
check(f"weak pitch scores strictly lower ({weak_overall} < {overall})", weak_overall < overall, True)

print("\n== the scorer is deterministic ==")
again = ai.score_pitch(pitch_text)
check("same input, same output", again == scores, True)

print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILED: {fails}"))
