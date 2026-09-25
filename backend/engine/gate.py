GATE_THRESHOLD = 6.0

def gate_decision(dimension_scores: list) -> tuple[bool, float]:
    total = sum(d.score for d in dimension_scores)
    avg = total / len(dimension_scores)
    passed = avg >= GATE_THRESHOLD
    return passed, avg