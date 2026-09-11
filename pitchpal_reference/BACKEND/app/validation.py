"""5-step validation engine with false-reject logging.

Pure functions, zero external deps. Rules are heuristics: deterministic,
auditable, zero AI APIs. Every failure is logged for weekly review (PRD §3.2).
"""

import re
from dataclasses import dataclass
from typing import Tuple

from app.models import ValidationFailure
from sqlalchemy.ext.asyncio import AsyncSession


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


PASS_COST = 2  # tokens per message, deducted server-side by /chat


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

_VALIDATORS = {
    1: "_validate_step1",
    2: "_validate_step2",
    3: "_validate_step3",
    4: "_validate_step4",
    5: "_validate_step5",
}


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


def _validate_step1(answer: str) -> Tuple[bool, str]:
    words = answer.split()
    if len(words) < _IDEA_MIN_WORDS:
        return False, _PUSHBACK[1]
    if not any(w.rstrip(".,!?") in _IDEA_VERBS for w in words):
        return False, _PUSHBACK[1]
    return True, ""


def _validate_step2(answer: str) -> Tuple[bool, str]:
    low = answer.lower()
    if not re.search(r"\d+", answer):
        return False, _PUSHBACK[2]
    if not _contains_any(low, _PAIN_WORDS):
        return False, _PUSHBACK[2]
    return True, ""


def _validate_step3(answer: str) -> Tuple[bool, str]:
    low = answer.lower()
    has_price = any(re.search(p, low) for p in _PRICE_PATTERNS)
    has_frequency = _contains_any(low, _FREQUENCY_WORDS)
    if not (has_price and has_frequency):
        return False, _PUSHBACK[3]
    return True, ""


def _validate_step4(answer: str) -> Tuple[bool, str]:
    low = answer.lower()
    if _count_competitor_names(answer) < 2:
        return False, _PUSHBACK[4]
    if not _contains_any(low, _DIFF_WORDS):
        return False, _PUSHBACK[4]
    return True, ""


def _validate_step5(answer: str) -> Tuple[bool, str]:
    low = answer.lower()
    if not _contains_any(low, _EXPERIENCE_WORDS):
        return False, _PUSHBACK[5]
    if not _contains_any(low, _ADVANTAGE_WORDS):
        return False, _PUSHBACK[5]
    return True, ""


def validate_answer(step: int, answer: str) -> Tuple[bool, str]:
    """Dispatch to the rule for this step. Returns (passed, pushback_text)."""
    validator_map = {
        1: _validate_step1,
        2: _validate_step2,
        3: _validate_step3,
        4: _validate_step4,
        5: _validate_step5,
    }
    return validator_map[step](answer)


async def log_validation_failure(
    db: AsyncSession,
    user_id: int,
    session_id: int,
    step: int,
    raw_answer: str,
    pushback_message: str,
) -> None:
    """Log a failed validation for false-reject analysis (PRD §3.2)."""
    failure = ValidationFailure(
        user_id=user_id,
        session_id=session_id,
        step=step,
        raw_answer=raw_answer,
        pushback_message=pushback_message,
    )
    db.add(failure)
    await db.commit()


def process_answer(step: int, answer: str) -> StepResult:
    """
    Core of the state machine. Called by /chat after the answer is stored.
    - Pass  -> moves to next step (or marks pitch complete after step 5)
    - Fail  -> pushback message, step stays the same, user retries
    """
    trimmed = (answer or "").strip()
    if not trimmed:
        return StepResult(
            passed=False,
            reply="You sent an empty answer. Say it out loud — then type it.",
            next_step=step,
        )

    passed, feedback = validate_answer(step, trimmed)
    if not passed:
        return StepResult(passed=False, reply=feedback, next_step=step)

    if step >= TOTAL_STEPS:
        return StepResult(passed=True, reply=COMPLETE_MESSAGE, next_step=TOTAL_STEPS)

    next_step = step + 1
    reply = TRANSITION_PRAISE.get(step, "") + STEP_QUESTIONS[next_step - 1]
    return StepResult(passed=True, reply=reply, next_step=next_step)


def get_step_question(step: int) -> str:
    """Return the question text for a 1-indexed step."""
    return STEP_QUESTIONS[step - 1]


def is_last_step(step: int) -> bool:
    return step >= TOTAL_STEPS


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
    print("OK")