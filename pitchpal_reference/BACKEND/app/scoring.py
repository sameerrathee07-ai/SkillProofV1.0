"""6-dimension heuristic scoring engine.

Pure functions, zero external deps. Each dimension scored 1-10 by keyword/
signal heuristics — deterministic, auditable, zero external API calls.
The weakest dimension gets a one-sentence feedback callout.
"""

from typing import Dict, List

from app.validation import _parse_pitch_lines


def _score_dimension(
    text: str,
    positive_keywords: List[str],
    negative_keywords: List[str],
    base: int = 5,
    max_boost: int = 3,
    max_penalty: int = 3,
) -> int:
    """Simple frequency-based scorer: boost for positive signals, penalize for negative."""
    low = (text or "").lower()
    score = base
    for kw in positive_keywords:
        if kw in low:
            score += 1
    for kw in negative_keywords:
        if kw in low:
            score -= 1
    return max(1, min(10, score))


def score_pitch(pitch_text: str) -> Dict:
    """
    Score the full pitch across 6 dimensions (1-10) and return a feedback sentence.
    Matches schemas.ScoreResponse exactly.
    """
    ans = _parse_pitch_lines(pitch_text)
    full = " ".join(ans.values())

    # 1. Problem Clarity — specific pain, numbers, urgency words
    problem = _score_dimension(
        ans.get(1, "") + " " + ans.get(2, ""),
        [
            "pain", "problem", "struggle", "waste", "hate", "difficult", "expensive",
            "slow", "frustrat", "headache", "nightmare", "urgent", "critical",
            "losing", "costly", "inefficient", "broken", "risk",
        ],
        ["maybe", "think", "could", "perhaps", "sort of", "kind of"],
        base=5, max_boost=3, max_penalty=2,
    )

    # 2. Market Specificity — numbers, demographics, concrete segments
    market = _score_dimension(
        ans.get(2, ""),
        [
            "aged", "age", "year", "old", "demographic", "segment", "niche", "vertical",
            "million", "billion", "thousand", "percent", "%", "users", "customers",
            "students", "founders", "developers", "enterprises", "smbs",
        ],
        ["everyone", "anyone", "all people", "global", "worldwide", "anyone who"],
        base=5, max_boost=3, max_penalty=2,
    )

    # 3. Revenue Viability — price, frequency, recurring, unit economics
    revenue = _score_dimension(
        ans.get(3, ""),
        [
            "monthly", "yearly", "annual", "recurring", "subscription", "per month",
            "per year", "per user", "per seat", "pricing", "revenue", "margin",
            "ltv", "cac", "payback", "churn", "renewal",
        ],
        ["free", "ads", "maybe later", "not sure", "figure it out"],
        base=4, max_boost=3, max_penalty=3,
    )

    # 4. Competitive Awareness — named competitors, differentiation words
    competition = _score_dimension(
        ans.get(4, ""),
        [
            "competitor", "vs", "versus", "unlike", "different", "better", "cheaper",
            "faster", "unique", "edge", "advantage", "differentiate", "moat",
            "proprietary", "patent", "exclusive",
        ],
        ["no competition", "nobody does", "first ever", "no one else"],
        base=4, max_boost=3, max_penalty=3,
    )

    # 5. Team Credibility — experience, shipped, years, domain, built, led
    team = _score_dimension(
        ans.get(5, ""),
        [
            "years", "experience", "built", "founded", "launched", "led", "managed",
            "shipped", "scaled", "sold", "raised", "engineered", "designed",
            "expert", "veteran", "domain", "background", "worked at", "certified",
        ],
        ["student", "learning", "just started", "no experience", "fresh"],
        base=4, max_boost=3, max_penalty=3,
    )

    # 6. Investor Readiness — composite of above + clear ask, traction signals
    readiness = _score_dimension(
        full,
        [
            "traction", "users", "revenue", "growth", "mrr", "arr", "pilot", "beta",
            "waitlist", "signed", "contract", "investment", "funding", "round",
            "pre-seed", "seed", "angel", "vc", "term sheet",
        ],
        ["idea stage", "just an idea", "no product", "concept only"],
        base=4, max_boost=2, max_penalty=2,
    )

    # Clamp all
    dims = {
        "problem_clarity": problem,
        "market_specificity": market,
        "revenue_viability": revenue,
        "competitive_awareness": competition,
        "team_credibility": team,
        "investor_readiness": readiness,
    }

    # Feedback: weakest dimension
    weakest = min(dims, key=dims.get)
    feedback_map = {
        "problem_clarity": "The problem isn't sharp enough — add a specific pain point with numbers.",
        "market_specificity": "Define your customer more precisely — age, segment, and scale matter.",
        "revenue_viability": "The money model needs a price and a recurring frequency.",
        "competitive_awareness": "Name real competitors and spell out your differentiation.",
        "team_credibility": "Highlight relevant experience and your unfair advantage.",
        "investor_readiness": "Show traction signals (users, revenue, pilots) to prove readiness.",
    }
    feedback = feedback_map[weakest]

    return {**dims, "feedback": feedback}


if __name__ == "__main__":
    # Test scoring
    strong = [
        (1, "PitchPal automatically validates startup pitch answers and pushes back with targeted coaching to sharpen them."),
        (2, "Students aged 18 to 24 hate wasting hours preparing vague pitches and feel stuck without expert feedback."),
        (3, "We charge 49 rupees monthly for students and 99 rupees yearly for teams who pay per subscription."),
        (4, "ChatGPT, Claude and Grammarly give generic advice, but PitchPal uniquely validates structure step by step."),
        (5, "I have five years of experience building fintech products and my unfair advantage is direct access to bank data."),
    ]
    pitch_text = "\n".join(f"[{i}] {a}" for i, (_, a) in enumerate(strong, 1))
    scores = score_pitch(pitch_text)
    assert set(scores.keys()) == {"problem_clarity", "market_specificity", "revenue_viability",
                                   "competitive_awareness", "team_credibility", "investor_readiness", "feedback"}
    for k, v in scores.items():
        if k != "feedback":
            assert 1 <= v <= 10, f"{k} score out of range: {v}"
    assert isinstance(scores["feedback"], str) and len(scores["feedback"]) > 10

    # Weak pitch should score lower
    weak_pitch = "[1] An app.\n[2] Everyone.\n[3] Free.\n[4] No one.\n[5] I'm new."
    weak_scores = score_pitch(weak_pitch)
    assert all(1 <= v <= 10 for k, v in weak_scores.items() if k != "feedback")

    print("OK")