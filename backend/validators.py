import re

# Action verbs for Step 1
_VERBS = {
    "helps", "help", "makes", "make", "builds", "build", "creates", "create",
    "connects", "connect", "automates", "automate", "saves", "save", "reduces",
    "reduce", "lets", "let", "allows", "allow", "turns", "turn", "replaces",
    "replace", "tracks", "track", "manages", "manage", "improves", "improve",
    "simplifies", "simplify", "solves", "solve", "teaches", "teach", "learns",
    "learn", "finds", "find", "matches", "match", "sells", "sell", "delivers",
    "deliver", "offers", "offer", "provides", "provide", "generates", "generate",
    "predicts", "predict", "analyzes", "analyze", "streamlines", "streamline",
    "removes", "remove", "eliminates", "eliminate", "speeds", "speed", "cuts",
    "cut", "organizes", "organize", "plans", "plan", "schedules", "schedule",
    "books", "book", "pays", "pay", "detects", "detect", "warns", "warn",
    "reminds", "remind", "summarizes", "summarize", "translates", "translate",
    "verifies", "verify", "validates", "validate", "checks", "check",
    "prevents", "prevent", "protects", "protect", "secures", "secure",
    "coaches", "coach", "trains", "train", "guides", "guide", "grades", "grade",
}

# Pain words for Step 2
_PAIN_WORDS = {
    "pain", "problem", "struggle", "hard", "waste", "wasting", "hate", "hated",
    "tired", "difficult", "expensive", "slow", "annoying", "broken", "worried",
    "stuck", "losing", "lose", "costly", "trouble", "frustrated", "frustration",
    "headache", "nightmare", "inconvenient", "inefficient", "confusion",
    "errors", "mistakes", "delays", "risk", "overwhelmed", "burnout", "stress",
    "stressful", "suffer", "unclear", "chaos", "overwhelming", "manual", "bottleneck"
}

# Price/Frequency patterns for Step 3
_PRICE_PATTERNS = [
    r"[$€£₹¥]",
    r"\d+\s*(?:rs|rupees|dollars|inr|usd|eur|pounds|euros|k|lakh|crore)\b",
    r"\b(?:price|pricing|cost|costs|charge|charges|fee|fees|priced|charged|budget|save|saves|roi)\b",
]
_FREQUENCY_WORDS = [
    "monthly", "yearly", "annually", "weekly", "daily", "quarterly",
    "per month", "per year", "per week", "per day", "per user", "per seat",
    "per hire", "per project", "per session", "subscription", "recurring",
    "one-time", "one time", "every month", "retainer", "per download", "per transaction"
]

# Differentiation words for Step 4
_DIFF_WORDS = [
    "different", "differentiate", "difference", "better", "cheaper", "faster",
    "unlike", "unique", "uniquely", "edge", "advantage", "vs", "versus",
    "instead", "compared", "more than", "whereas", "we do", "not just", "approach", "custom"
]

_CAP_IGNORE = {
    "i", "my", "we", "our", "the", "a", "an", "it", "this", "that", "these",
    "those", "they", "their", "he", "she", "you", "your", "but", "and", "so",
    "because", "when", "where", "why", "what", "how", "there", "here", "then",
    "me", "us", "one", "two", "most", "more", "much", "also", "even", "just",
    "only", "not", "no", "yes", "if", "some", "other", "another", "every",
    "each", "first", "second", "last", "at", "in", "on", "of", "for", "with",
    "to", "from", "as", "while", "after", "before", "like", "such"
}

# Experience/Advantage words for Step 5
_EXPERIENCE_WORDS = [
    "experience", "worked", "working", "built", "founded", "launched", "led",
    "managed", "shipped", "years", "background", "degree", "studied",
    "interned", "trained", "certified", "i've", "i have", "we built",
    "developed", "engineered", "designed", "grew", "scaled", "sold", "raised",
    "operated", "team", "previous", "earlier"
]
_ADVANTAGE_WORDS = [
    "advantage", "unfair", "unique", "edge", "access", "network", "relationships",
    "domain", "expertise", "insight", "patent", "patents", "data", "moat",
    "hard to copy", "distribution", "audience", "following", "community",
    "insider", "proprietary", "first mover", "exclusive", "experience"
]

def has_verb(text: str) -> bool:
    words = [w.strip(".,!?").lower() for w in text.split()]
    return any(w in _VERBS for w in words)

def has_currency_reference(text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in _PRICE_PATTERNS)

def has_timeline_reference(text: str) -> bool:
    low = text.lower()
    return any(word in low for word in ["week", "month", "day", "year", "date", "by", "deadline", "quarter"])

def count_words(text: str) -> int:
    return len(text.strip().split())

def validate_problem_description(text: str) -> tuple[bool, str]:
    if count_words(text) < 15:
        return False, "Problem description must be at least 15 words so solvers have enough context."
    if not has_verb(text):
        return False, "Problem description must contain a clear action verb explaining what is happening or broken."
    return True, ""

def validate_pitch_step(step: int, answer: str) -> tuple[bool, str]:
    trimmed = answer.strip()
    if not trimmed:
        return False, "You sent an empty answer. Please articulate your response."

    if step == 1:
        if count_words(trimmed) < 10:
            return False, "Step 1 requires at least 10 words. Explain what your solution does."
        if not has_verb(trimmed):
            return False, "Step 1 must include an action verb (e.g., automates, reduces, solves, builds, connects)."
        return True, ""

    elif step == 2:
        low = trimmed.lower()
        if not re.search(r"\d+", trimmed) and not any(w in low for w in ["manager", "team", "staff", "guest", "client", "user", "customer", "people"]):
            return False, "Step 2 requires specifying who faces this (number, age, or specific team/role)."
        if not any(k in low for k in _PAIN_WORDS):
            return False, "Step 2 must mention their specific pain point or bottleneck (e.g., manual, slow, struggle, waste, loss)."
        return True, ""

    elif step == 3:
        low = trimmed.lower()
        has_price = any(re.search(p, low) for p in _PRICE_PATTERNS)
        has_frequency = any(f in low for f in _FREQUENCY_WORDS)
        if not (has_price or has_frequency):
            return False, "Step 3 must include price/cost numbers or currency references (₹, $, etc.) and frequency/value justification."
        return True, ""

    elif step == 4:
        low = trimmed.lower()
        if not any(d in low for d in _DIFF_WORDS):
            return False, "Step 4 must state 2+ alternatives or competitors and explain why your approach is better or unique."
        return True, ""

    elif step == 5:
        low = trimmed.lower()
        if not any(e in low for e in _EXPERIENCE_WORDS):
            return False, "Step 5 must state your relevant experience, background, or past projects."
        if not any(a in low for a in _ADVANTAGE_WORDS):
            return False, "Step 5 must highlight your unfair advantage or domain edge."
        return True, ""

    return True, ""
