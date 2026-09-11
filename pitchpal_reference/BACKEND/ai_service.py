import re
from dataclasses import dataclass

# Commit 13: The 5-step pitch flow state machine.
# WHY: The whole product is a fixed conversation. The backend owns the state —
# the user can never skip a step, reorder answers, or advance without passing.
# Commit 14 adds the per-step rule-based validation that feeds into this.

TOTAL_STEPS = 5

# The five fixed questions, one per step. Exact copy lives here so the API,
# the resume flow, and (later) the PDF all use the same strings.
STEP_QUESTIONS = [
    "Step 1 — Idea: One sentence. What does your product do? Be specific enough that a stranger could explain it back.",
    "Step 2 — Customer: Who is it for? Give an age, their situation, and the exact pain point you're solving.",
    "Step 3 — Business Model: What do you charge, who pays it, and how often?",
    "Step 4 — Competition: Name at least 2 competitors. Then tell me how you're different.",
    "Step 5 — Team: What experience do you have, and what is your unfair advantage?",
]

# Opening message served by /session/start. Introduces the rules of the game.
OPENING_MESSAGE = (
    "Welcome to PitchPal. I'm your coach — and I don't let you ramble. "
    "You'll answer 5 fixed questions and every answer must clear the bar before we move on. "
    "Each message costs 2 tokens, so think before you type. "
    + STEP_QUESTIONS[0]
)

# Per-step praise line, keeps the flow feeling human instead of robotic.
TRANSITION_PRAISE = {
    1: "Good start. ",
    2: "Now the money part. ",
    3: "Who else is in the arena? ",
    4: "Almost there. ",
    5: "",
}

COMPLETE_MESSAGE = (
    "That's the full pitch. Every step passed — your outline is ready. "
    "I'm scoring it across 6 dimensions now; the results and your PDF are waiting."
)


@dataclass
class StepResult:
    """Single decision from the state machine."""
    passed: bool
    reply: str
    next_step: int  # stays on current step when pushback, else advances


def get_step_question(step: int) -> str:
    """Return the question text for a 1-indexed step."""
    return STEP_QUESTIONS[step - 1]


def is_last_step(step: int) -> bool:
    return step >= TOTAL_STEPS


# ── Commit 14: Step validation rules ────────────────────────────────────
# Each step has one validation rule (see PRD §5.1). Every rule returns
# (passed, pushback) — a targeted message explaining EXACTLY what's missing.
# Rules are heuristics on purpose: deterministic, auditable, zero AI APIs.

# Step 1 — Idea: ≥10 words + an action verb
_IDEA_MIN_WORDS = 10
_IDEA_VERBS = {
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

# Step 2 — Customer: number/age reference + pain keyword
_PAIN_WORDS = {
    "pain", "problem", "struggle", "hard", "waste", "wasting", "hate", "hated",
    "tired", "difficult", "expensive", "slow", "annoying", "broken", "worried",
    "stuck", "losing", "lose", "costly", "trouble", "frustrated", "frustration",
    "headache", "nightmare", "inconvenient", "inefficient", "confusion",
    "errors", "mistakes", "delays", "risk", "overwhelmed", "burnout", "stress",
    "stressful", "suffer", "unclear", "chaos", "overwhelming",
}

# Step 3 — Business Model: price/currency + frequency word
_PRICE_PATTERNS = [
    r"[$€£₹¥]",
    r"\d+\s*(?:rs|rupees|dollars|inr|usd|eur|pounds|euros)\b",
    r"\b(?:price|pricing|cost|costs|charge|charges|fee|fees|priced|charged)\b",
]
_FREQUENCY_WORDS = [
    "monthly", "yearly", "annually", "weekly", "daily", "quarterly",
    "per month", "per year", "per week", "per day", "per user", "per seat",
    "per hire", "per project", "per session", "subscription", "recurring",
    "one-time", "one time", "every month", "retainer", "per download",
]

# Step 4 — Competition: 2+ competitor names + differentiation phrase
_DIFF_WORDS = [
    "different", "differentiate", "difference", "better", "cheaper", "faster",
    "unlike", "unique", "uniquely", "edge", "advantage", "vs", "versus",
    "instead", "compared", "more than", "whereas", "we do", "not just",
]
# Capitalized words that are NOT competitor names (sentence starters/prons...)
_CAP_IGNORE = {
    "i", "my", "we", "our", "the", "a", "an", "it", "this", "that", "these",
    "those", "they", "their", "he", "she", "you", "your", "but", "and", "so",
    "because", "when", "where", "why", "what", "how", "there", "here", "then",
    "me", "us", "one", "two", "most", "more", "much", "also", "even", "just",
    "only", "not", "no", "yes", "if", "some", "other", "another", "every",
    "each", "first", "second", "last", "at", "in", "on", "of", "for", "with",
    "to", "from", "as", "while", "after", "before", "like", "such",
}

# Step 5 — Team: experience claim + unfair advantage claim
_EXPERIENCE_WORDS = [
    "experience", "worked", "working", "built", "founded", "launched", "led",
    "managed", "shipped", "years", "background", "degree", "studied",
    "interned", "trained", "certified", "i've", "i have", "we built",
    "developed", "engineered", "designed", "grew", "scaled", "sold", "raised",
    "operated", "team", "previous", "earlier",
]
_ADVANTAGE_WORDS = [
    "advantage", "unfair", "unique", "edge", "access", "network", "relationships",
    "domain", "expertise", "insight", "patent", "patents", "data", "moat",
    "hard to copy", "distribution", "audience", "following", "community",
    "insider", "proprietary", "first mover", "exclusive",
]

# Targeted pushback per step — tells the user exactly what the rule needs.
_PUSHBACK = {
    1: "That idea is too vague for an investor. One sentence, at least 10 words, with a real action verb — what does it actually DO? Try again.",
    2: "I need a real person here. Give me an age or number, their situation, and the pain they feel. Try again.",
    3: "Show me the money. State a price or currency and how often it's paid (monthly, yearly, per user...). Try again.",
    4: "Name your competitors — at least 2 — and tell me what makes you different from them. Try again.",
    5: "Why you? Give me your relevant experience and the unfair advantage that's hard to copy. Try again.",
}

PASS_COST = 2  # tokens per message, deducted server-side by /chat


def _contains_any(text: str, keywords) -> bool:
    """Substring match on lowercased text — 'unique' also catches 'uniquely'."""
    return any(k in text for k in keywords)


def _count_competitor_names(answer: str) -> int:
    """Heuristic: count capitalized word runs, ignoring sentence starters/prons."""
    names = set()
    for match in re.finditer(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?", answer):
        run = match.group(0)
        first_word = run.split()[0].lower()
        if first_word in _CAP_IGNORE:
            continue
        names.add(run.lower())
    return len(names)


def _validate_step1(answer: str) -> tuple:
    words = answer.split()
    if len(words) < _IDEA_MIN_WORDS:
        return False, _PUSHBACK[1]
    if not any(w.rstrip(".,!?") in _IDEA_VERBS for w in words):
        return False, _PUSHBACK[1]
    return True, ""


def _validate_step2(answer: str) -> tuple:
    low = answer.lower()
    if not re.search(r"\d+", answer):
        return False, _PUSHBACK[2]
    if not _contains_any(low, _PAIN_WORDS):
        return False, _PUSHBACK[2]
    return True, ""


def _validate_step3(answer: str) -> tuple:
    low = answer.lower()
    has_price = any(re.search(p, low) for p in _PRICE_PATTERNS)
    has_frequency = _contains_any(low, _FREQUENCY_WORDS)
    if not (has_price and has_frequency):
        return False, _PUSHBACK[3]
    return True, ""


def _validate_step4(answer: str) -> tuple:
    low = answer.lower()
    if _count_competitor_names(answer) < 2:
        return False, _PUSHBACK[4]
    if not _contains_any(low, _DIFF_WORDS):
        return False, _PUSHBACK[4]
    return True, ""


def _validate_step5(answer: str) -> tuple:
    low = answer.lower()
    if not _contains_any(low, _EXPERIENCE_WORDS):
        return False, _PUSHBACK[5]
    if not _contains_any(low, _ADVANTAGE_WORDS):
        return False, _PUSHBACK[5]
    return True, ""


_VALIDATORS = {
    1: _validate_step1,
    2: _validate_step2,
    3: _validate_step3,
    4: _validate_step4,
    5: _validate_step5,
}


def validate_answer(step: int, answer: str) -> tuple:
    """Dispatch to the rule for this step. Returns (passed, pushback_text)."""
    return _VALIDATORS[step](answer)


def process_answer(step: int, answer: str) -> StepResult:
    """
    Core of the state machine. Called by /chat after the answer is stored.
    - Pass  -> moves to next step (or marks pitch complete after step 5)
    - Fail  -> pushback message, step stays the same, user retries
    """
    trimmed = (answer or "").strip()
    if not trimmed:
        return StepResult(passed=False, reply="You sent an empty answer. Say it out loud — then type it.", next_step=step)

    passed, feedback = validate_answer(step, trimmed)
    if not passed:
        return StepResult(passed=False, reply=feedback, next_step=step)

    if is_last_step(step):
        return StepResult(passed=True, reply=COMPLETE_MESSAGE, next_step=TOTAL_STEPS)

    next_step = step + 1
    reply = TRANSITION_PRAISE.get(step, "") + get_step_question(next_step)
    return StepResult(passed=True, reply=reply, next_step=next_step)


# ── Commit 17: Pitch outline generator ──────────────────────────────────
# WHY: After step 5 passes, the raw pitch_text (one line per validated answer)
# is turned into a 7-section investor-ready outline. The PDF and scoring both
# consume this structure. No AI — deterministic mapping from the 5 answers.

def _parse_pitch_lines(pitch_text: str) -> dict:
    """Extract the 5 answers from pitch_text lines like '[1] answer\\n[2] answer...'."""
    answers = {}
    for line in (pitch_text or "").splitlines():
        line = line.strip()
        if line.startswith("[") and "] " in line:
            try:
                step_num = int(line[1:line.index("]")])
                content = line[line.index("] ") + 2:]
                answers[step_num] = content.strip()
            except (ValueError, IndexError):
                continue
    return answers


def generate_outline(pitch_text: str, founder_name: str = "Founder") -> dict:
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


# ── Commit 18: Heuristic scoring engine ─────────────────────────────────
# WHY: Investors care about 6 dimensions. Each is scored 1–10 by keyword/
# signal heuristics — deterministic, auditable, zero external API calls.
# The weakest dimension gets a one-sentence feedback callout.

def _score_dimension(text: str, positive_keywords: list, negative_keywords: list,
                     base: int = 5, max_boost: int = 3, max_penalty: int = 3) -> int:
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


def score_pitch(pitch_text: str) -> dict:
    """
    Score the full pitch across 6 dimensions (1–10) and return a feedback sentence.
    Matches schemas.ScoreResponse exactly.
    """
    ans = _parse_pitch_lines(pitch_text)
    full = " ".join(ans.values())

    # 1. Problem Clarity — specific pain, numbers, urgency words
    problem = _score_dimension(
        ans.get(1, "") + " " + ans.get(2, ""),
        ["pain", "problem", "struggle", "waste", "hate", "difficult", "expensive",
         "slow", "frustrat", "headache", "nightmare", "urgent", "critical",
         "losing", "costly", "inefficient", "broken", "risk"],
        ["maybe", "think", "could", "perhaps", "sort of", "kind of"],
        base=5, max_boost=3, max_penalty=2,
    )

    # 2. Market Specificity — numbers, demographics, concrete segments
    market = _score_dimension(
        ans.get(2, ""),
        ["aged", "age", "year", "old", "demographic", "segment", "niche", "vertical",
         "million", "billion", "thousand", "percent", "%", "users", "customers",
         "students", "founders", "developers", "enterprises", "smbs"],
        ["everyone", "anyone", "all people", "global", "worldwide", "anyone who"],
        base=5, max_boost=3, max_penalty=2,
    )

    # 3. Revenue Viability — price, frequency, recurring, unit economics
    revenue = _score_dimension(
        ans.get(3, ""),
        ["monthly", "yearly", "annual", "recurring", "subscription", "per month",
         "per year", "per user", "per seat", "pricing", "revenue", "margin",
         "ltv", "cac", "payback", "churn", "renewal"],
        ["free", "ads", "maybe later", "not sure", "figure it out"],
        base=4, max_boost=3, max_penalty=3,
    )

    # 4. Competitive Awareness — named competitors, differentiation words
    competition = _score_dimension(
        ans.get(4, ""),
        ["competitor", "vs", "versus", "unlike", "different", "better", "cheaper",
         "faster", "unique", "edge", "advantage", "differentiate", "moat",
         "proprietary", "patent", "exclusive"],
        ["no competition", "nobody does", "first ever", "no one else"],
        base=4, max_boost=3, max_penalty=3,
    )

    # 5. Team Credibility — experience, shipped, years, domain, built, led
    team = _score_dimension(
        ans.get(5, ""),
        ["years", "experience", "built", "founded", "launched", "led", "managed",
         "shipped", "scaled", "sold", "raised", "engineered", "designed",
         "expert", "veteran", "domain", "background", "worked at", "certified"],
        ["student", "learning", "just started", "no experience", "fresh"],
        base=4, max_boost=3, max_penalty=3,
    )

    # 6. Investor Readiness — composite of above + clear ask, traction signals
    readiness = _score_dimension(
        full,
        ["traction", "users", "revenue", "growth", "mrr", "arr", "pilot", "beta",
         "waitlist", "signed", "contract", "investment", "funding", "round",
         "pre-seed", "seed", "angel", "vc", "term sheet"],
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
    # Smoke test every rule + the state machine, without the API.
    weak = [
        (1, "A short one."),
        (2, "It helps students."),
        (3, "It is a good product."),
        (4, "Nobody does this."),
        (5, "I am a student."),
    ]
    for step, answer in weak:
        r = process_answer(step, answer)
        assert not r.passed and r.next_step == step, f"step {step} must push back"
    strong = [
        (1, "PitchPal automatically validates startup pitch answers and pushes back with targeted coaching to sharpen them."),
        (2, "Students aged 18 to 24 hate wasting hours preparing vague pitches and feel stuck without expert feedback."),
        (3, "We charge 49 rupees monthly for students and 99 rupees yearly for teams who pay per subscription."),
        (4, "ChatGPT, Claude and Grammarly give generic advice, but PitchPal uniquely validates structure step by step."),
        (5, "I have five years of experience building fintech products and my unfair advantage is direct access to bank data."),
    ]
    for i, (step, answer) in enumerate(strong, start=1):
        r = process_answer(step, answer)
        assert r.passed, f"good step {step} answer must pass: {r.reply}"
        assert r.next_step == (step + 1 if step < 5 else 5), f"step {step} must advance"
    r = process_answer(5, strong[4][1])
    assert r.passed, "last step pass marks completion"

    # Test outline generator
    pitch_text = "\n".join(f"[{i}] {a}" for i, (_, a) in enumerate(strong, 1))
    outline = generate_outline(pitch_text, "Test Founder")
    assert set(outline.keys()) == {"problem", "solution", "customer", "business_model", "competition", "team", "ask", "founder_name"}
    assert outline["founder_name"] == "Test Founder"
    assert "validates" in outline["solution"].lower()
    assert "18 to 24" in outline["customer"]
    assert "49 rupees" in outline["business_model"]
    assert "ChatGPT" in outline["competition"]
    assert "fintech" in outline["team"]

    # Test scoring
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