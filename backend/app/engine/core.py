import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Step(int, Enum):
    IDEA = 1
    CUSTOMER = 2
    COST_VALUE = 3
    ALTERNATIVES = 4
    SOLVER = 5


IDEA_VERBS = {
    "automate", "automates", "automated", "automatically", "automating",
    "schedule", "schedules", "scheduled", "scheduling",
    "alert", "alerts", "alerted", "alerting",
    "optimize", "optimizes", "optimized", "optimizing",
    "reduce", "reduces", "reduced", "reducing",
    "eliminate", "eliminates", "eliminated", "eliminating",
    "streamline", "streamlines", "streamlined", "streamlining",
    "improve", "improves", "improved", "improving",
    "accelerate", "accelerates", "accelerated", "accelerating",
    "simplify", "simplifies", "simplified", "simplifying",
    "integrate", "integrates", "integrated", "integrating",
    "connect", "connects", "connected", "connecting",
    "manage", "manages", "managed", "managing",
    "track", "tracks", "tracked", "tracking",
    "monitor", "monitors", "monitored", "monitoring",
    "analyze", "analyzes", "analyzed", "analyzing",
    "predict", "predicts", "predicted", "predicting",
    "generate", "generates", "generated", "generating",
    "create", "creates", "created", "creating",
    "build", "builds", "built", "building",
    "design", "designs", "designed", "designing",
    "develop", "develops", "developed", "developing",
    "implement", "implements", "implemented", "implementing",
    "deploy", "deploys", "deployed", "deploying",
    "launch", "launches", "launched", "launching",
    "scale", "scales", "scaled", "scaling",
    "enhance", "enhances", "enhanced", "enhancing",
    "transform", "transforms", "transformed", "transforming",
    "modernize", "modernizes", "modernized", "modernizing",
    "digitize", "digitizes", "digitized", "digitizing",
    "centralize", "centralizes", "centralized", "centralizing",
    "standardize", "standardizes", "standardized", "standardizing",
    "orchestrate", "orchestrates", "orchestrated", "orchestrating",
    "coordinate", "coordinates", "coordinated", "coordinating"
}

ROLE_WORDS = {
    "manager", "managers", "director", "directors", "lead", "leads", "head", "heads", "chief", "chiefs", "vp", "vice president", "supervisor", "supervisors",
    "coordinator", "coordinators", "specialist", "specialists", "analyst", "analysts", "associate", "associates", "assistant", "assistants", "officer", "officers",
    "executive", "executives", "admin", "administrator", "administrators", "operator", "operators", "agent", "agents", "representative", "representatives",
    "clerk", "clerks", "staff", "team", "teams", "department", "departments", "division", "divisions", "branch", "branches", "unit", "units", "group", "groups",
    "front desk", "front-desk", "reception", "housekeeping", "maintenance", "kitchen", "service",
    "sales", "marketing", "finance", "accounting", "hr", "human resources", "it",
    "engineering", "development", "product", "operations", "logistics", "supply chain"
}

PAIN_KEYWORDS = {
    "pain", "problem", "problems", "issue", "issues", "challenge", "challenges", "difficulty", "difficulties", "struggle", "struggles", "frustrat",
    "waste", "wastes", "wasted", "costly", "expensive", "slow", "delay", "delays", "delayed", "error", "errors", "mistake", "mistakes", "inefficient",
    "manual", "tedious", "repetitive", "bottleneck", "bottlenecks", "overwhelm", "overwhelmed", "burnout", "stress", "stresses", "stressed",
    "lost", "miss", "misses", "missed", "fail", "fails", "failed", "break", "breaks", "broken", "downtime", "complaint", "complaints", "unhappy", "dissatisfied"
}

PRICE_PATTERNS = [
    r"(?:rs|inr|rupees?|₹)\s*\d+",
    r"\$\s*\d+",
    r"\d+\s*(?:rs|inr|rupees?|₹|\$)",
    r"\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:per\s+(?:month|year|user|hotel|property))?",
]

JUSTIFICATION_WORDS = {
    "save", "saves", "saving", "reduce", "reduces", "reducing", "payback", "roi",
    "return", "justify", "worth", "value", "benefit", "gain", "improve", "improves",
    "per month", "per year", "per user", "per hotel", "per property", "instead of",
    "compared to", "versus", "vs", "cheaper", "faster", "better", "efficient"
}

APPROACH_PHRASES = {
    "manual process", "spreadsheet", "existing software", "outsourcing",
    "current system", "legacy system", "paper based", "paper-based",
    "manual entry", "manual tracking", "manual scheduling", "manual coordination"
}

DIFFERENTIATION_WORDS = {
    "vs", "versus", "unlike", "instead of", "better than", "compared to",
    "different from", "different", "superior to", "outperforms", "beats", "advantage over",
    "edge over", "improves on", "enhances", "replaces", "alternative to"
}

EXPERIENCE_WORDS = {
    "built", "shipped", "deployed", "managed", "led", "created", "developed",
    "designed", "implemented", "launched", "delivered", "completed", "finished",
    "intern", "internship", "project", "experience", "worked", "worked on",
    "contributed", "maintained", "operated", "ran", "ran a", "founded", "co-founded"
}

ADVANTAGE_WORDS = {
    "advantage", "edge", "unique", "differentiator", "moat", "proprietary",
    "exclusive", "specialized", "expertise", "knowledge", "access", "network",
    "relationship", "partnership", "patent", "ip", "intellectual property",
    "insider", "firsthand", "direct", "personal", "family", "own", "test"
}

DELIVERY_WORDS = {
    "pilot", "prototype", "mvp", "demo", "timeline", "week", "month", "milestone",
    "phase", "stage", "deliver", "delivery", "ready", "available", "launch",
    "release", "deploy", "implement", "rollout", "schedule", "plan", "roadmap"
}

NEGATIVE_HEDGING = {"maybe", "kind of", "sort of", "somehow", "possibly", "perhaps", "might", "could be"}
NEGATIVE_BROAD = {"everyone", "global", "all people", "everybody", "anyone", "whole world"}
NEGATIVE_COST = {"free", "not sure", "depends", "unknown", "unclear", "tbd", "to be determined"}
NEGATIVE_ALT = {"no competition", "nobody does", "first ever", "no alternative", "unique", "only one"}
NEGATIVE_EXP = {"just started", "no experience", "never done", "beginner", "novice", "fresh"}
NEGATIVE_DELIVERY = {"just an idea", "concept only", "theoretical", "not started", "no plan"}

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "as", "is", "was", "are", "were", "be", "been", "being", "have",
    "has", "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "must", "can", "this", "that", "these", "those", "i", "you", "he",
    "she", "it", "we", "they", "my", "your", "his", "her", "its", "our", "their",
    "me", "him", "us", "them", "mine", "yours", "hers", "ours", "theirs", "am",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "can", "shall", "ought", "need", "dare", "used", "use", "using"
}


@dataclass
class StepResult:
    passed: bool
    reply: str
    next_step: int


COMPLETE_MESSAGE = "All steps complete. Your pitch is ready for scoring."

PUSHBACK_MESSAGES = {
    Step.IDEA: "Add a specific action verb (e.g., automate, schedule, optimize) and at least 10 words describing what your solution does.",
    Step.CUSTOMER: "Name the exact role or team facing this problem and describe their specific pain (e.g., front-desk managers lose hours reassigning rooms).",
    Step.COST_VALUE: "State a price in Rs (or $) and justify it (e.g., saves 40 hours/month, pays back in 1 month).",
    Step.ALTERNATIVES: "Name at least 2 alternative approaches (e.g., Excel sheets, Opera PMS add-ons) and explain why yours is better using comparison words (vs, unlike, instead of).",
    Step.SOLVER: "Cite relevant experience (built, shipped, intern, project) and your unfair advantage (family hotel for testing, proprietary access, unique expertise).",
}


def _word_boundary_match(text: str, word_set: set) -> List[str]:
    found = []
    text_lower = text.lower()
    for word in word_set:
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(word)
    return found


def _count_words(text: str) -> int:
    return len(text.strip().split())


def _has_price(text: str) -> bool:
    text_lower = text.lower()
    for pattern in PRICE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False


def _extract_alternatives(text: str) -> List[str]:
    alternatives = []
    text_lower = text.lower()
    
    for phrase in APPROACH_PHRASES:
        if phrase in text_lower:
            alternatives.append(phrase)
    
    words = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', text)
    for word in words:
        if word.lower() not in STOPWORDS and len(word) > 2:
            alternatives.append(word)
    
    seen = set()
    unique = []
    for alt in alternatives:
        key = alt.lower()
        if key not in seen:
            seen.add(key)
            unique.append(alt)
    return unique


def validate_step(step: Step, answer: str) -> Tuple[bool, str]:
    answer = answer.strip()
    if not answer:
        return False, "Answer cannot be empty."
    
    if len(answer) > 5000:
        return False, "Answer exceeds 5000 character limit."
    
    if step == Step.IDEA:
        word_count = _count_words(answer)
        verbs_found = _word_boundary_match(answer, IDEA_VERBS)
        if word_count < 10 or not verbs_found:
            return False, PUSHBACK_MESSAGES[step]
        return True, "Good — clear, action-oriented idea."
    
    elif step == Step.CUSTOMER:
        roles_found = _word_boundary_match(answer, ROLE_WORDS)
        pain_found = _word_boundary_match(answer, PAIN_KEYWORDS)
        has_number = bool(re.search(r'\b\d+\b', answer))
        if not (roles_found or has_number) or not pain_found:
            return False, PUSHBACK_MESSAGES[step]
        return True, "Good — specific role and pain identified."
    
    elif step == Step.COST_VALUE:
        has_price = _has_price(answer)
        just_found = _word_boundary_match(answer, JUSTIFICATION_WORDS)
        if not has_price or not just_found:
            return False, PUSHBACK_MESSAGES[step]
        return True, "Good — price and justification provided."
    
    elif step == Step.ALTERNATIVES:
        alternatives = _extract_alternatives(answer)
        diff_found = _word_boundary_match(answer, DIFFERENTIATION_WORDS)
        if len(alternatives) < 2 or not diff_found:
            return False, PUSHBACK_MESSAGES[step]
        return True, "Good — alternatives named and differentiated."
    
    elif step == Step.SOLVER:
        exp_found = _word_boundary_match(answer, EXPERIENCE_WORDS)
        adv_found = _word_boundary_match(answer, ADVANTAGE_WORDS)
        if not exp_found or not adv_found:
            return False, PUSHBACK_MESSAGES[step]
        return True, "Good — experience and advantage claimed."
    
    return False, "Unknown step."


def process_answer(current_step: int, answer: str) -> StepResult:
    step = Step(current_step)
    passed, reply = validate_step(step, answer)
    
    if passed:
        if step == Step.SOLVER:
            return StepResult(True, reply + " " + COMPLETE_MESSAGE, 5)
        return StepResult(True, reply, step + 1)
    else:
        return StepResult(False, reply, step)


def _parse_pitch_lines(pitch_text: str) -> Dict[int, str]:
    result = {}
    lines = pitch_text.strip().split('\n')
    for line in lines:
        match = re.match(r'\[(\d+)\]\s*(.*)', line.strip())
        if match:
            step_num = int(match.group(1))
            answer = match.group(2).strip()
            if 1 <= step_num <= 5:
                result[step_num] = answer
    return result


DIMENSION_CONFIG = {
    "Problem Clarity": {
        "steps": [1, 2],
        "base": 5,
        "max_boost": 3,
        "max_penalty": 2,
        "positive": {"pain", "waste", "costly", "urgent", "delay", "error"},
        "negative": {"maybe", "kind of", "sort of", "somehow", "possibly", "perhaps"},
    },
    "Customer Specificity": {
        "steps": [2],
        "base": 5,
        "max_boost": 3,
        "max_penalty": 2,
        "positive": {"manager", "staff", "front desk", "branch", "department", "segment"},
        "negative": {"everyone", "global", "all people", "everybody", "anyone"},
    },
    "Cost and Value Case": {
        "steps": [3],
        "base": 4,
        "max_boost": 3,
        "max_penalty": 3,
        "positive": {"per month", "one-time", "saves", "payback", "roi", "per user"},
        "negative": {"free", "not sure", "depends", "unknown", "unclear"},
    },
    "Alternatives Awareness": {
        "steps": [4],
        "base": 4,
        "max_boost": 3,
        "max_penalty": 3,
        "positive": {"vs", "unlike", "instead of", "better than", "compared to"},
        "negative": {"no competition", "nobody does", "first ever", "no alternative"},
    },
    "Solver Capability": {
        "steps": [5],
        "base": 4,
        "max_boost": 3,
        "max_penalty": 3,
        "positive": {"built", "shipped", "deployed", "managed", "intern", "project"},
        "negative": {"just started", "no experience", "never done", "beginner", "novice"},
    },
    "Delivery Readiness": {
        "steps": [1, 2, 3, 4, 5],
        "base": 4,
        "max_boost": 2,
        "max_penalty": 2,
        "positive": {"pilot", "prototype", "timeline", "weeks", "milestone", "demo"},
        "negative": {"just an idea", "concept only", "theoretical", "not started", "no plan"},
    },
}

DIMENSION_ORDER = [
    "Problem Clarity",
    "Customer Specificity",
    "Cost and Value Case",
    "Alternatives Awareness",
    "Solver Capability",
    "Delivery Readiness",
]


def _score_dimension(text: str, config: dict) -> Tuple[int, List[str], List[str]]:
    text_lower = text.lower()
    pos_found = set()
    neg_found = set()
    
    for word in config["positive"]:
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, text_lower):
            pos_found.add(word)
    
    for word in config["negative"]:
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, text_lower):
            neg_found.add(word)
    
    boost = min(len(pos_found), config["max_boost"])
    penalty = min(len(neg_found), config["max_penalty"])
    
    score = config["base"] + boost - penalty
    score = max(1, min(10, score))
    
    return score, list(pos_found), list(neg_found)


def score_pitch(pitch_text: str) -> Tuple[Dict[str, int], str]:
    answers = _parse_pitch_lines(pitch_text)
    full_text = " ".join(answers.values())
    
    scores = {}
    pos_details = {}
    neg_details = {}
    
    for dim_name in DIMENSION_ORDER:
        config = DIMENSION_CONFIG[dim_name]
        step_texts = []
        for step_num in config["steps"]:
            if step_num in answers:
                step_texts.append(answers[step_num])
        combined_text = " ".join(step_texts) if step_texts else full_text
        
        score, pos, neg = _score_dimension(combined_text, config)
        scores[dim_name] = score
        pos_details[dim_name] = pos
        neg_details[dim_name] = neg
    
    min_score = min(scores.values())
    weakest = [d for d in DIMENSION_ORDER if scores[d] == min_score][0]
    
    feedback = generate_suggestion(weakest, answers, pos_details.get(weakest, []), neg_details.get(weakest, []))
    
    return scores, feedback


def generate_suggestion(dim: str, answers: Dict[int, str], pos: List[str], neg: List[str]) -> str:
    suggestions = {
        "Problem Clarity": "Name the concrete cost of the problem (delay, waste, errors) and remove hedging such as maybe or kind of.",
        "Customer Specificity": "Name the exact role or team and how many people are affected.",
        "Cost and Value Case": "State a price in Rs and justify it against the cost of the problem (for example hours saved per month).",
        "Alternatives Awareness": "Name two alternative approaches and say specifically why yours is better.",
        "Solver Capability": "Cite one project, role or asset that makes you able to deliver this.",
        "Delivery Readiness": "Add a delivery timeline and one milestone the company can check.",
    }
    return suggestions.get(dim, "Improve this dimension.")


def gate_decision(scores: Dict[str, int], threshold: float = 6.0) -> Tuple[bool, float]:
    avg = sum(scores.values()) / len(scores)
    return avg >= threshold, avg


def generate_outline(answers: Dict[int, str], solver_name: str = "Solver") -> Dict[str, str]:
    defaults = {
        1: "Solution not provided.",
        2: "Affected people not specified.",
        3: "Cost and value not specified.",
        4: "Alternatives not specified.",
        5: "Solver background not specified.",
    }
    
    return {
        "Problem": answers.get(1, defaults[1]).split('.')[0] + '.' if answers.get(1) else defaults[1],
        "Solution": answers.get(1, defaults[1]),
        "Affected People": answers.get(2, defaults[2]),
        "Cost and Value": answers.get(3, defaults[3]),
        "Alternatives and Edge": answers.get(4, defaults[4]),
        "Solver and Advantage": answers.get(5, defaults[5]),
        "Proposed Next Step": "Proposed next step: a short call to agree scope and timeline.",
    }


def compute_credibility(proposals: List[dict]) -> dict:
    if not proposals:
        return {
            "avg_gate_score": 0.0,
            "first_attempt_passes": 0,
            "total_attempts": 0,
            "total_passes": 0,
        }
    
    passed = [p for p in proposals if p.get("status") == "submitted"]
    first_attempt = [p for p in passed if p.get("attempts", 1) == 1]
    
    avg_gate = sum(p.get("gate_score", 0) for p in passed) / len(passed) if passed else 0.0
    
    return {
        "avg_gate_score": round(avg_gate, 2),
        "first_attempt_passes": len(first_attempt),
        "total_attempts": len(proposals),
        "total_passes": len(passed),
    }