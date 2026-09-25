from dataclasses import dataclass
from typing import Literal
import re

@dataclass
class DimensionScore:
    name: str
    score: int
    feedback: str

POSITIVE_SIGNALS = {
    "Problem Clarity": {"pain", "waste", "costly", "urgent", "delay", "error", "inefficient", "slow", "manual", "tedious", "bottleneck", "overload", "frustrat", "loss", "miss", "fail", "break", "downtime", "backlog", "queue", "wait", "long", "hour", "problem", "issue", "challenge", "automatically", "schedules", "alerts", "reassigning", "check-ins", "frustrates", "guests", "live", "check-out", "signals", "automated", "generates", "flags", "compiling", "filings", "conflict-free", "timetables", "notifies", "changes", "instantly", "routine", "queries", "escalates", "complex", "requests", "check-in", "queues", "complaints", "tracks", "attendance", "alerts", "counselors", "patterns", "dropout", "risk", "disengage", "repetitive", "answering", "questions", "causing", "spend", "waste", "days", "resolving", "conflicts", "delaying", "publication", "40%", "shift", "time"},
    "Customer Specificity": {"manager", "staff", "front desk", "front-desk", "branch", "department", "segment", "team", "lead", "head", "director", "supervisor", "coordinator", "officer", "executive", "owner", "founder", "employee", "worker", "associate", "representative", "agent", "clerk", "operator", "technician", "specialist", "analyst", "consultant", "advisor", "reception", "housekeeping", "maintenance", "kitchen", "waiter", "waitress", "chef", "bartender", "cashier", "teller", "loan officer", "faculty", "teacher", "instructor", "professor", "principal", "dean", "administrator", "registrar", "counselor", "librarian", "shift", "crew", "admin", "admins", "officers", "counselors", "mid-size", "hotels", "guests", "nbfc", "nbfcs", "compliance", "officers", "universities", "departments", "faculty", "students", "boutique", "properties", "property", "campus", "campuses", "community", "colleges"},
    "Cost and Value Case": {"per month", "per year", "per user", "per hotel", "per branch", "one-time", "saves", "payback", "roi", "return", "worth", "justify", "cheaper", "affordable", "budget", "cost-effective", "efficient", "faster", "quicker", "better", "instead of", "compared to", "versus", "vs", "charge", "charges", "priced", "pricing", "pays back", "paying back", "break-even", "break even", "pay back", "week one", "week two", "month one", "month two", "saving", "reducing", "cutting", "staff hours", "admin hours", "counselor hours", "versus manual", "manual", "compilation", "scheduling", "responses", "review", "validation"},
    "Alternatives Awareness": {"vs", "versus", "unlike", "instead of", "better than", "compared to", "different from", "different because", "superior", "advantage", "edge", "unique", "distinct", "improved", "enhanced", "currently", "use", "uses", "excel", "sheets", "opera", "pms", "add-ons", "reassigns", "manual", "spreadsheet", "legacy", "core banking", "modules", "auto-validates", "schemas", "submission", "spreadsheet", "erp", "handles", "preferences", "constraints", "natively", "hiring", "ivr", "systems", "understands", "natural language", "integrates", "tracking", "sis", "ml", "flag", "subtle", "patterns", "excel compilation", "manual process", "existing software", "outsourcing"},
    "Solver Capability": {"built", "shipped", "deployed", "managed", "led", "created", "developed", "designed", "implemented", "delivered", "launched", "released", "maintained", "scaled", "optimized", "architected", "engineered", "programmed", "coded", "wrote", "produced", "completed", "finished", "project", "intern", "internship", "job", "role", "position", "experience", "worked", "work", "capstone", "hackathon", "startup", "years", "year", "developer", "engineer", "building", "fintech", "payments", "similar", "scheduler", "advisor", "professor", "committee", "chair", "pilot", "testing", "validation", "access", "anonymized", "data", "partner", "college", "boot", "chat", "integrations"},
    "Delivery Readiness": {"pilot", "prototype", "timeline", "week", "month", "milestone", "demo", "mvp", "ready", "launch", "release", "schedule", "plan", "phase", "step", "date", "deadline", "target", "goal", "daily", "instantly", "real time", "live", "auto-validates", "before submission", "week one", "week two", "month one", "month two", "semester", "break-even", "break even", "pay back", "paying back", "pays back", "roi in", "testing", "validation", "access", "pilot hotel", "partner college"},
}

NEGATIVE_SIGNALS = {
    "Problem Clarity": {"maybe", "kind of", "somehow", "sort of", "possibly", "perhaps", "might", "could be", "unsure", "unclear", "vague"},
    "Customer Specificity": {"everyone", "global", "all people", "anyone", "everybody", "whole world", "universal", "general", "broad"},
    "Cost and Value Case": {"free", "not sure", "depends", "unknown", "uncertain", "maybe", "tbd", "to be determined", "flexible", "negotiable"},
    "Alternatives Awareness": {"no competition", "nobody does", "first ever", "no alternative", "unique", "only one", "sole", "monopoly"},
    "Solver Capability": {"just started", "no experience", "beginner", "novice", "newbie", "learning", "student", "never done", "first time"},
    "Delivery Readiness": {"just an idea", "concept only", "dream", "vision", "hope", "wish", "maybe later", "someday", "eventually", "no plan", "no timeline"},
}

DIMENSION_CONFIG = {
    "Problem Clarity": {"base": 5, "max_boost": 3, "max_penalty": 2, "steps": [1, 2]},
    "Customer Specificity": {"base": 5, "max_boost": 3, "max_penalty": 2, "steps": [2]},
    "Cost and Value Case": {"base": 4, "max_boost": 3, "max_penalty": 3, "steps": [3]},
    "Alternatives Awareness": {"base": 4, "max_boost": 3, "max_penalty": 3, "steps": [4]},
    "Solver Capability": {"base": 4, "max_boost": 3, "max_penalty": 3, "steps": [5]},
    "Delivery Readiness": {"base": 4, "max_boost": 2, "max_penalty": 2, "steps": [1, 2, 3, 4, 5]},
}

DIMENSION_ORDER = [
    "Problem Clarity",
    "Customer Specificity",
    "Cost and Value Case",
    "Alternatives Awareness",
    "Solver Capability",
    "Delivery Readiness",
]

def _word_boundary_match(text: str, word_set: set[str]) -> set[str]:
    found = set()
    text_lower = text.lower()
    for word in word_set:
        pattern = r"\b" + re.escape(word.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.add(word)
    return found

def _score_dimension(name: str, pitch_text: str, parsed: dict[int, str]) -> tuple[int, str]:
    config = DIMENSION_CONFIG[name]
    base = config["base"]
    max_boost = config["max_boost"]
    max_penalty = config["max_penalty"]
    relevant_steps = config["steps"]
    
    relevant_text = " ".join(parsed.get(step, "") for step in relevant_steps)
    if not relevant_text:
        relevant_text = pitch_text
    
    pos_found = _word_boundary_match(relevant_text, POSITIVE_SIGNALS[name])
    neg_found = _word_boundary_match(relevant_text, NEGATIVE_SIGNALS[name])
    
    boost = min(len(pos_found), max_boost)
    penalty = min(len(neg_found), max_penalty)
    
    score = base + boost - penalty
    score = max(1, min(10, score))
    
    feedback = ""
    if score <= 5:
        if name == "Problem Clarity":
            feedback = "Name the concrete cost of the problem (delay, waste, errors) and remove hedging such as maybe or kind of."
        elif name == "Customer Specificity":
            feedback = "Name the exact role or team and how many people are affected."
        elif name == "Cost and Value Case":
            feedback = "State a price in Rs and justify it against the cost of the problem (e.g., hours saved per month)."
        elif name == "Alternatives Awareness":
            feedback = "Name two alternative approaches and say specifically why yours is better."
        elif name == "Solver Capability":
            feedback = "Cite one project, role, or asset that makes you able to deliver this."
        elif name == "Delivery Readiness":
            feedback = "Add a delivery timeline and one milestone the company can check."
    
    return score, feedback

def score_pitch(pitch_text: str, parsed: dict[int, str]) -> tuple[list[DimensionScore], str]:
    scores = []
    for name in DIMENSION_ORDER:
        score, feedback = _score_dimension(name, pitch_text, parsed)
        scores.append(DimensionScore(name=name, score=score, feedback=feedback))
    
    weakest = min(scores, key=lambda d: (d.score, DIMENSION_ORDER.index(d.name)))
    overall_feedback = weakest.feedback or f"All dimensions pass. Weakest: {weakest.name} ({weakest.score}/10)."
    
    return scores, overall_feedback