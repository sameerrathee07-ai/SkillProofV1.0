from typing import Optional
from .scoring import DimensionScore

SUGGESTIONS = {
    "Problem Clarity": "Name the concrete cost of the problem (delay, waste, errors) and remove hedging such as maybe or kind of.",
    "Customer Specificity": "Name the exact role or team and how many people are affected.",
    "Cost and Value Case": "State a price in Rs and justify it against the cost of the problem (e.g., hours saved per month).",
    "Alternatives Awareness": "Name two alternative approaches and say specifically why yours is better.",
    "Solver Capability": "Cite one project, role, or asset that makes you able to deliver this.",
    "Delivery Readiness": "Add a delivery timeline and one milestone the company can check.",
}

def generate_suggestions(dimension_scores: list[DimensionScore]) -> dict[str, str]:
    return {d.name: SUGGESTIONS.get(d.name, "") for d in dimension_scores}