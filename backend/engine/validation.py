import re
from dataclasses import dataclass
from typing import Literal

IDEA_VERBS = {"build", "create", "design", "develop", "implement", "automate", "optimize", "streamline", "reduce", "eliminate", "improve", "solve", "fix", "address", "tackle", "deliver", "provide", "enable", "allow", "connect", "integrate", "schedule", "assign", "track", "monitor", "alert", "notify", "generate", "calculate", "analyze", "report", "manage", "organize", "coordinate", "simplify", "standardize", "digitize", "modernize", "replace", "upgrade", "enhance", "automatically", "schedules", "generates", "flags", "creates", "handles", "escalates", "tracks", "alerts", "notifies", "compiles", "validates", "resolves", "creates", "notifies"}

ROLE_WORDS = {"manager", "managers", "staff", "team", "lead", "head", "director", "supervisor", "coordinator", "officer", "executive", "owner", "founder", "employee", "worker", "associate", "representative", "agent", "clerk", "operator", "technician", "specialist", "analyst", "consultant", "advisor", "front desk", "front-desk", "reception", "housekeeping", "maintenance", "kitchen", "waiter", "waitress", "chef", "bartender", "cashier", "teller", "loan officer", "branch", "department", "division", "unit", "section", "floor", "shift", "crew", "faculty", "teacher", "instructor", "professor", "principal", "dean", "administrator", "registrar", "counselor", "librarian", "ta", "ra", "student", "intern", "admin", "admins", "officer", "officers", "counselor", "counselors"}

PAIN_KEYWORDS = {"pain", "problem", "issue", "challenge", "difficulty", "struggle", "frustrat", "frustrat", "waste", "loss", "cost", "delay", "error", "mistake", "inefficient", "slow", "manual", "tedious", "repetitive", "bottleneck", "overload", "burnout", "complain", "unhappy", "dissatisfied", "angry", "stress", "pressure", "burden", "headache", "nightmare", "mess", "chaos", "confusion", "miss", "fail", "break", "downtime", "outage", "backlog", "queue", "wait", "long", "hour", "day", "week", "month", "frustrates", "frustrating", "frustration", "delays", "delaying", "wastes", "wasting", "costs", "costing", "loses", "losing"}

PRICE_PATTERNS = [
    r"(?:rs|inr|rupees?|₹)\s*\d+",
    r"\d+\s*(?:rs|inr|rupees?|₹)",
    r"\$\s*\d+",
    r"\d+\s*\$",
    r"\d+(?:,\d{3})*(?:\.\d{2})?",
]

JUSTIFICATION_WORDS = {"save", "saves", "reduces", "reduce", "cut", "cuts", "payback", "roi", "return", "worth", "justify", "justifies", "per month", "per year", "per user", "per hotel", "per branch", "instead of", "compared to", "versus", "vs", "cheaper", "cheapest", "affordable", "budget", "cost-effective", "efficient", "faster", "quicker", "better", "saving", "saving", "reducing", "cutting", "break-even", "break even", "pay back", "paying back", "pays back"}

ALTERNATIVE_PHRASES = {"manual process", "spreadsheet", "existing software", "outsourcing", "current system", "legacy system", "paper", "pen and paper", "whiteboard", "email", "phone", "call", "meeting", "word of mouth", "walk-in", "paper-based", "excel", "google sheets", "notion", "trello", "asana", "jira", "slack", "teams", "whatsapp"}

DIFFERENTIATION_WORDS = {"vs", "versus", "unlike", "instead of", "better than", "compared to", "different from", "different because", "superior", "advantage", "edge", "unique", "distinct", "improved", "enhanced", "faster", "cheaper", "simpler", "easier", "more", "differs", "differs from", "unlike", "rather than"}

EXPERIENCE_WORDS = {"built", "shipped", "deployed", "managed", "led", "created", "developed", "designed", "implemented", "delivered", "launched", "released", "maintained", "scaled", "optimized", "architected", "engineered", "programmed", "coded", "wrote", "produced", "completed", "finished", "project", "intern", "internship", "job", "role", "position", "experience", "worked", "work", "capstone", "hackathon", "startup", "years", "year", "developer", "engineer", "built", "building"}

ADVANTAGE_WORDS = {"advantage", "edge", "unique", "special", "different", "insider", "access", "network", "connection", "relationship", "knowledge", "expertise", "skill", "background", "experience", "family", "friend", "partner", "contact", "mentor", "advisor", "investor", "customer", "client", "user", "test", "pilot", "prototype", "demo", "mvp", "early", "first", "direct", "personal", "advisor", "professor", "committee", "chair", "own", "runs", "operates"}

STOPWORDS = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "as", "is", "was", "are", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "my", "your", "his", "her", "its", "our", "their", "me", "him", "us", "them", "mine", "yours", "hers", "ours", "theirs"}

@dataclass
class StepResult:
    passed: bool
    reply: str
    next_step: int

COMPLETE_MESSAGE = "All steps complete. Your pitch is ready for scoring."

def _word_boundary_match(text: str, word_set: set[str]) -> set[str]:
    found = set()
    text_lower = text.lower()
    for word in word_set:
        pattern = r"\b" + re.escape(word.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.add(word)
    return found

def _count_words(text: str) -> int:
    return len(text.split())

def _has_action_verb(text: str, verb_set: set[str]) -> bool:
    return bool(_word_boundary_match(text, verb_set))

def _has_price(text: str) -> bool:
    text_lower = text.lower()
    for pattern in PRICE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def _extract_alternatives(text: str) -> set[str]:
    alts = set()
    text_lower = text.lower()
    for phrase in ALTERNATIVE_PHRASES:
        if re.search(r"\b" + re.escape(phrase) + r"\b", text_lower):
            alts.add(phrase)
    words = re.findall(r"\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b", text)
    for word in words:
        if word.lower() not in STOPWORDS and len(word) > 2:
            alts.add(word)
    return alts

def validate_step1(answer: str) -> StepResult:
    answer = answer.strip()
    if not answer:
        return StepResult(False, "Answer cannot be empty. Describe your solution in one sentence.", 1)
    if len(answer) > 5000:
        return StepResult(False, "Answer too long (max 5000 characters).", 1)
    if _count_words(answer) < 10:
        return StepResult(False, "Answer must be at least 10 words. Be more specific.", 1)
    if not _has_action_verb(answer, IDEA_VERBS):
        return StepResult(False, "Include at least one action verb (e.g., build, create, automate, reduce, streamline).", 1)
    return StepResult(True, "Good — clear solution statement. Step 2: Who faces this problem and what is their pain?", 2)

def validate_step2(answer: str) -> StepResult:
    answer = answer.strip()
    if not answer:
        return StepResult(False, "Answer cannot be empty. Name the role/team and their pain.", 2)
    if len(answer) > 5000:
        return StepResult(False, "Answer too long (max 5000 characters).", 2)
    roles_found = _word_boundary_match(answer, ROLE_WORDS)
    pain_found = _word_boundary_match(answer, PAIN_KEYWORDS)
    if not roles_found:
        return StepResult(False, "Name the specific role or team (e.g., front-desk managers, branch staff, faculty).", 2)
    if not pain_found:
        return StepResult(False, "Describe the pain (e.g., waste, delay, error, frustration, hours lost).", 2)
    return StepResult(True, "Good — specific role and pain identified. Step 3: What will it cost and how is that justified?", 3)

def validate_step3(answer: str) -> StepResult:
    answer = answer.strip()
    if not answer:
        return StepResult(False, "Answer cannot be empty. State a price and justification.", 3)
    if len(answer) > 5000:
        return StepResult(False, "Answer too long (max 5000 characters).", 3)
    if not _has_price(answer):
        return StepResult(False, "Include a price (e.g., Rs 4,999/month, $99, 5000 rupees).", 3)
    just_found = _word_boundary_match(answer, JUSTIFICATION_WORDS)
    if not just_found:
        return StepResult(False, "Justify the cost (e.g., saves 40 hrs/month, pays back in 1 month, ROI).", 3)
    return StepResult(True, "Good — cost and value case made. Step 4: Name at least 2 alternatives and why yours is better.", 4)

def validate_step4(answer: str) -> StepResult:
    answer = answer.strip()
    if not answer:
        return StepResult(False, "Answer cannot be empty. Name alternatives and your edge.", 4)
    if len(answer) > 5000:
        return StepResult(False, "Answer too long (max 5000 characters).", 4)
    alts = _extract_alternatives(answer)
    if len(alts) < 2:
        return StepResult(False, "Name at least 2 distinct alternatives (e.g., Excel, manual process, existing software, outsourcing).", 4)
    diff_found = _word_boundary_match(answer, DIFFERENTIATION_WORDS)
    if not diff_found:
        return StepResult(False, "Explain why yours is better (e.g., vs, unlike, instead of, better than, compared to).", 4)
    return StepResult(True, "Good — alternatives and differentiation clear. Step 5: What is your experience and unfair advantage?", 5)

def validate_step5(answer: str) -> StepResult:
    answer = answer.strip()
    if not answer:
        return StepResult(False, "Answer cannot be empty. Cite experience and advantage.", 5)
    if len(answer) > 5000:
        return StepResult(False, "Answer too long (max 5000 characters).", 5)
    exp_found = _word_boundary_match(answer, EXPERIENCE_WORDS)
    adv_found = _word_boundary_match(answer, ADVANTAGE_WORDS)
    if not exp_found:
        return StepResult(False, "Cite relevant experience (e.g., built, shipped, intern, project, managed).", 5)
    if not adv_found:
        return StepResult(False, "Name your unfair advantage (e.g., family hotel for testing, insider access, unique skill).", 5)
    return StepResult(True, COMPLETE_MESSAGE, 5)

VALIDATORS = {
    1: validate_step1,
    2: validate_step2,
    3: validate_step3,
    4: validate_step4,
    5: validate_step5,
}

def process_answer(step: int, answer: str) -> StepResult:
    if step not in VALIDATORS:
        return StepResult(False, "Invalid step.", step)
    return VALIDATORS[step](answer)