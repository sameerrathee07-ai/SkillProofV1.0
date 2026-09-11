import re
from typing import Dict, Any

def _score_dimension(text: str, positive_keywords: list, negative_keywords: list,
                     base: int = 5) -> int:
    low = (text or "").lower()
    score = base
    for kw in positive_keywords:
        if kw in low:
            score += 1
    for kw in negative_keywords:
        if kw in low:
            score -= 1
    return max(1, min(10, score))

def score_pitch_responses(responses: Dict[str, str]) -> Dict[str, Any]:
    """
    Evaluates 5 pitch responses across 6 dimensions.
    Returns individual dimension scores (1-10), average score, pass/fail status (gate threshold >= 6.0),
    and targeted feedback for the weakest dimension.
    """
    step1 = responses.get("step1", "")
    step2 = responses.get("step2", "")
    step3 = responses.get("step3", "")
    step4 = responses.get("step4", "")
    step5 = responses.get("step5", "")
    full_text = f"{step1} {step2} {step3} {step4} {step5}"

    # 1. Problem Clarity
    problem_clarity = _score_dimension(
        step1 + " " + step2,
        ["pain", "problem", "struggle", "waste", "difficult", "expensive", "slow", "frustration", "manual", "bottleneck", "reduce", "automate", "solve"],
        ["maybe", "think", "could", "perhaps", "sort of", "kind of"],
        base=6
    )

    # 2. Market Specificity
    market_specificity = _score_dimension(
        step2,
        ["aged", "age", "year", "team", "staff", "manager", "hotel", "bank", "client", "guest", "student", "user", "customer", "percent", "%", "daily", "monthly"],
        ["everyone", "anyone", "all people", "global"],
        base=6
    )

    # 3. Revenue Viability
    revenue_viability = _score_dimension(
        step3,
        ["monthly", "yearly", "annual", "recurring", "subscription", "per month", "price", "cost", "save", "roi", "value", "margin", "inr", "usd", "rs", "₹", "$"],
        ["free", "ads", "not sure", "figure it out"],
        base=5
    )

    # 4. Competitive Awareness
    competitive_awareness = _score_dimension(
        step4,
        ["competitor", "vs", "versus", "unlike", "different", "better", "cheaper", "faster", "unique", "edge", "advantage", "alternative", "custom", "existing"],
        ["no competition", "nobody does", "first ever", "no one"],
        base=5
    )

    # 5. Team Credibility
    team_credibility = _score_dimension(
        step5,
        ["years", "experience", "built", "founded", "launched", "led", "managed", "shipped", "engineered", "designed", "expert", "background", "project", "degree"],
        ["student", "learning", "just started", "no experience"],
        base=5
    )

    # 6. Investor Readiness
    investor_readiness = _score_dimension(
        full_text,
        ["traction", "users", "revenue", "growth", "pilot", "beta", "ready", "prototype", "architecture", "timeline", "deliverable"],
        ["idea stage", "just an idea", "concept only"],
        base=5
    )

    dims = {
        "problem_clarity": problem_clarity,
        "market_specificity": market_specificity,
        "revenue_viability": revenue_viability,
        "competitive_awareness": competitive_awareness,
        "team_credibility": team_credibility,
        "investor_readiness": investor_readiness,
    }

    avg_score = round(sum(dims.values()) / 6.0, 1)

    # Identify weakest dimension
    weakest = min(dims, key=dims.get)
    feedback_map = {
        "problem_clarity": "Problem Clarity is low — articulate the core operational bottleneck with more specificity.",
        "market_specificity": "Market Specificity needs improvement — identify the exact team, role, or demographic feeling the pain.",
        "revenue_viability": "Revenue Viability was low — include specific numbers, currency, or quantifiable time/cost savings.",
        "competitive_awareness": "Competitive Awareness needs work — list 2+ alternative solutions or current workarounds and your edge.",
        "team_credibility": "Team Credibility scored lowest — detail your relevant technical/domain background or past projects.",
        "investor_readiness": "Investor Readiness needs boost — articulate clear implementation steps and readiness signals.",
    }

    status = "submitted" if avg_score >= 6.0 else "needs_work"

    return {
        "dimension_scores": dims,
        "average_score": avg_score,
        "status": status,
        "feedback": feedback_map[weakest] if status == "needs_work" else "Pitch passed the quality gate successfully!"
    }
