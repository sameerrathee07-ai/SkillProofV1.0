"""7-section pitch outline generator.

Pure functions, zero external deps. Deterministic mapping from the 5
validated answers to an investor-ready outline. No AI.
"""

from typing import Dict

from app.validation import _parse_pitch_lines


def generate_outline(pitch_text: str, founder_name: str = "Founder") -> Dict:
    """
    Build the 7-section pitch outline from the 5 validated answers.
    Returns a dict with keys: problem, solution, customer, business_model,
    competition, team, ask.
    """
    ans = _parse_pitch_lines(pitch_text)

    return {
        "problem": ans.get(1, "").split(".")[0] + "." if ans.get(1) else "The problem is implied by the solution.",
        "solution": ans.get(1, "Our solution addresses the problem."),
        "customer": ans.get(2, "Target customer not specified."),
        "business_model": ans.get(3, "Business model not specified."),
        "competition": ans.get(4, "Competitive landscape not specified."),
        "team": ans.get(5, "Team background not specified."),
        "ask": "Seeking investment to accelerate growth and capture market share.",
        "founder_name": founder_name,
    }


if __name__ == "__main__":
    # Test outline generator
    strong = [
        (1, "PitchPal automatically validates startup pitch answers and pushes back with targeted coaching to sharpen them."),
        (2, "Students aged 18 to 24 hate wasting hours preparing vague pitches and feel stuck without expert feedback."),
        (3, "We charge 49 rupees monthly for students and 99 rupees yearly for teams who pay per subscription."),
        (4, "ChatGPT, Claude and Grammarly give generic advice, but PitchPal uniquely validates structure step by step."),
        (5, "I have five years of experience building fintech products and my unfair advantage is direct access to bank data."),
    ]
    pitch_text = "\n".join(f"[{i}] {a}" for i, (_, a) in enumerate(strong, 1))
    outline = generate_outline(pitch_text, "Test Founder")
    assert set(outline.keys()) == {"problem", "solution", "customer", "business_model", "competition", "team", "ask", "founder_name"}
    assert outline["founder_name"] == "Test Founder"
    assert "validates" in outline["solution"].lower()
    assert "18 to 24" in outline["customer"]
    assert "49 rupees" in outline["business_model"]
    assert "ChatGPT" in outline["competition"]
    assert "fintech" in outline["team"]
    print("OK")