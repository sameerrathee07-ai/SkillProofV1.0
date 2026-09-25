from .parser import parse_pitch_lines

DEFAULT_PROBLEM = "Problem not specified."
DEFAULT_SOLUTION = "Solution not specified."
DEFAULT_AFFECTED = "Affected people not specified."
DEFAULT_COST = "Cost and value not specified."
DEFAULT_ALTERNATIVES = "Alternatives not specified."
DEFAULT_SOLVER = "Solver not specified."
DEFAULT_ADVANTAGE = "Advantage not specified."
DEFAULT_NEXT_STEP = "Proposed next step: a short call to agree scope and timeline."

def generate_outline(pitch_text: str, solver_name: str = "Solver") -> dict[str, str]:
    parsed = parse_pitch_lines(pitch_text)
    
    step1 = parsed.get(1, "").strip()
    step2 = parsed.get(2, "").strip()
    step3 = parsed.get(3, "").strip()
    step4 = parsed.get(4, "").strip()
    step5 = parsed.get(5, "").strip()
    
    problem = step1.split(".")[0] + "." if step1 else DEFAULT_PROBLEM
    solution = step1 if step1 else DEFAULT_SOLUTION
    affected = step2 if step2 else DEFAULT_AFFECTED
    cost_value = step3 if step3 else DEFAULT_COST
    alternatives = step4 if step4 else DEFAULT_ALTERNATIVES
    
    solver_part = ""
    advantage_part = ""
    if step5:
        parts = step5.split(".", 1)
        solver_part = parts[0].strip()
        advantage_part = parts[1].strip() if len(parts) > 1 else ""
    solver_part = solver_part if solver_part else DEFAULT_SOLVER
    advantage_part = advantage_part if advantage_part else DEFAULT_ADVANTAGE
    
    return {
        "Problem": problem,
        "Solution": solution,
        "Affected People": affected,
        "Cost and Value": cost_value,
        "Alternatives and Edge": alternatives,
        "Solver and Advantage": f"{solver_part}. {advantage_part}",
        "Proposed Next Step": DEFAULT_NEXT_STEP,
        "solver_name": solver_name,
    }