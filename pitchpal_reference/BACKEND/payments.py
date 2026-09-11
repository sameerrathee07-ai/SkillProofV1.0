"""
The payment catalogue: packs, subscriptions, methods, promotions, currencies.

This module is the ONLY place prices exist. The frontend renders what it is
told and never computes money — a client-side discount is a client-side
decision, and a determined user can edit it before it reaches the server.

Money is held in minor units (paise, cents) as integers. A 20% discount on
₹99 is 9900 → 7920, not 99 * 0.8 with float drift, and every rounding
decision happens here rather than in three different callers.

Nothing in this file credits tokens. Crediting happens in routers/tokens.py
and stays disabled until a gateway webhook confirms a real payment.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple


# ── Currencies ────────────────────────────────────────────
# Regional pricing is a table of published list prices, not a live FX
# conversion. Charging a rate we invented at request time would mean the
# price moved between the pricing page and the checkout button.

@dataclass(frozen=True)
class Currency:
    code: str
    symbol: str
    locale: str
    decimals: int


CURRENCIES: Dict[str, Currency] = {
    "INR": Currency("INR", "₹", "en-IN", 0),
    "USD": Currency("USD", "$", "en-US", 2),
    "EUR": Currency("EUR", "€", "de-DE", 2),
    "GBP": Currency("GBP", "£", "en-GB", 2),
    "SGD": Currency("SGD", "S$", "en-SG", 2),
}

DEFAULT_CURRENCY = "INR"


def resolve_currency(code: Optional[str]) -> Currency:
    """Fall back to INR rather than 400 — an unknown locale should still see prices."""
    return CURRENCIES.get((code or "").upper(), CURRENCIES[DEFAULT_CURRENCY])


def format_amount(minor: int, currency: Currency) -> str:
    """Render minor units for display. The server formats money so the
    client cannot disagree about what it is being asked to pay."""
    if currency.decimals == 0:
        return f"{currency.symbol}{minor // 100:,}"
    major = minor / (10 ** currency.decimals)
    return f"{currency.symbol}{major:,.{currency.decimals}f}"


# ── Plans ─────────────────────────────────────────────────

ONE_TIME = "one_time"
SUBSCRIPTION = "subscription"


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    kind: str
    tokens: int                     # tokens granted per billing interval
    description: str
    badge: str = ""
    popular: bool = False
    interval: Optional[str] = None   # None | "month" | "year"
    prices: Dict[str, int] = field(default_factory=dict)  # currency -> minor units

    @property
    def months(self) -> int:
        return 12 if self.interval == "year" else 1

    @property
    def tokens_per_month(self) -> int:
        return self.tokens // self.months

    def price_minor(self, currency: Currency) -> int:
        # Every plan carries an INR price; other currencies are optional and
        # fall back rather than KeyError-ing a pricing page into a 500.
        return self.prices.get(currency.code, self.prices[DEFAULT_CURRENCY])


# Tokens the coach charges per answered step, mirrored from ai_service.PASS_COST.
TOKENS_PER_MESSAGE = 2
# A full pitch is 5 answered steps.
TOKENS_PER_PITCH = TOKENS_PER_MESSAGE * 5


def _pitches(tokens: int) -> str:
    whole = tokens // TOKENS_PER_PITCH
    return f"{whole} full pitch{'es' if whole != 1 else ''}"


PLANS: Tuple[Plan, ...] = (
    # ── Tiered one-time packs ──
    Plan(
        id="starter", name="Starter", kind=ONE_TIME, tokens=20,
        description=f"{_pitches(20)} — for a first run.",
        badge="First-time users",
        prices={"INR": 4900, "USD": 99, "EUR": 99, "GBP": 89, "SGD": 129},
    ),
    Plan(
        id="standard", name="Standard", kind=ONE_TIME, tokens=50,
        description=f"{_pitches(50)} — room to iterate.",
        badge="Regular pitchers", popular=True,
        prices={"INR": 9900, "USD": 199, "EUR": 199, "GBP": 179, "SGD": 269},
    ),
    Plan(
        id="pro", name="Pro", kind=ONE_TIME, tokens=100,
        description=f"{_pitches(100)} — rewrite until it lands.",
        badge="Active founders",
        prices={"INR": 17900, "USD": 349, "EUR": 349, "GBP": 299, "SGD": 479},
    ),
    Plan(
        id="team", name="Team", kind=ONE_TIME, tokens=250,
        description=f"{_pitches(250)} — a cohort's worth.",
        badge="Accelerators & teams",
        prices={"INR": 39900, "USD": 799, "EUR": 799, "GBP": 699, "SGD": 1099},
    ),

    # ── Recurring plans ──
    Plan(
        id="monthly-light", name="Light Monthly", kind=SUBSCRIPTION, tokens=30,
        interval="month", description="30 tokens every month. Cancel anytime.",
        badge="Flexible",
        prices={"INR": 7900, "USD": 149, "EUR": 149, "GBP": 129, "SGD": 199},
    ),
    Plan(
        id="monthly-standard", name="Standard Monthly", kind=SUBSCRIPTION, tokens=60,
        interval="month", description="60 tokens every month. Cancel anytime.",
        badge="Most popular", popular=True,
        prices={"INR": 14900, "USD": 299, "EUR": 299, "GBP": 249, "SGD": 399},
    ),
    Plan(
        id="monthly-heavy", name="Heavy Monthly", kind=SUBSCRIPTION, tokens=120,
        interval="month", description="120 tokens every month. Cancel anytime.",
        badge="Power user",
        prices={"INR": 24900, "USD": 499, "EUR": 499, "GBP": 429, "SGD": 669},
    ),
    Plan(
        # 720 tokens a year is the same 60 a month, billed once at ten months'
        # price — the "two months free" is the discount, so it carries no promo.
        id="yearly-standard", name="Standard Yearly", kind=SUBSCRIPTION, tokens=720,
        interval="year", description="60 tokens a month, billed yearly. Two months free.",
        badge="Best value",
        prices={"INR": 149000, "USD": 2990, "EUR": 2990, "GBP": 2490, "SGD": 3990},
    ),
)

PLANS_BY_ID: Dict[str, Plan] = {p.id: p for p in PLANS}

# The pack ids were basic/standard/pro before the Team tier landed. Keep the old
# names resolvable so an in-flight client or stored reference doesn't 400.
LEGACY_PLAN_ALIASES = {"basic": "starter"}


def get_plan(plan_id: Optional[str]) -> Optional[Plan]:
    key = (plan_id or "").strip().lower()
    return PLANS_BY_ID.get(LEGACY_PLAN_ALIASES.get(key, key))


def plans_of_kind(kind: str) -> List[Plan]:
    """Cheapest first, by INR list price, so the client renders without sorting."""
    return sorted(
        (p for p in PLANS if p.kind == kind),
        key=lambda p: p.prices[DEFAULT_CURRENCY],
    )


# ── Payment methods ───────────────────────────────────────
# `min_amount_inr` gates a method on the order total. EMI on a ₹49 pack is not
# a thing, and offering it then failing at the gateway is worse than not
# offering it, so eligibility is decided here and sent with the quote.

@dataclass(frozen=True)
class PaymentMethod:
    id: str
    name: str
    description: str
    icon: str
    min_amount_inr: int = 0


PAYMENT_METHODS: Tuple[PaymentMethod, ...] = (
    PaymentMethod("upi", "UPI", "PhonePe, GPay, Paytm — instant, no fee", "smartphone"),
    PaymentMethod("card", "Card", "Visa, Mastercard, RuPay", "creditCard"),
    PaymentMethod("netbanking", "Net banking", "50+ banks", "bank"),
    PaymentMethod("wallet", "Wallets", "Paytm, PhonePe, Amazon Pay", "wallet"),
    PaymentMethod("emi", "EMI", "3, 6, 9 or 12 months on cards", "calendar", min_amount_inr=3000),
)

EMI_TENURES = (3, 6, 9, 12)


def eligible_methods(amount_minor: int, currency: Currency) -> List[PaymentMethod]:
    """EMI and other floor-gated methods only apply to INR orders above their
    threshold; the floors are quoted by the Indian acquirer, not universal."""
    out = []
    for method in PAYMENT_METHODS:
        if method.min_amount_inr:
            if currency.code != DEFAULT_CURRENCY:
                continue
            if amount_minor < method.min_amount_inr * 100:
                continue
        out.append(method)
    return out


# ── Promotions ────────────────────────────────────────────

PERCENTAGE = "percentage"
FIXED = "fixed"


@dataclass(frozen=True)
class Promotion:
    code: str
    kind: str                    # PERCENTAGE | FIXED
    value: int                   # percent, or minor units in INR for FIXED
    description: str
    applies_to: Tuple[str, ...] = (ONE_TIME, SUBSCRIPTION)
    plan_ids: Tuple[str, ...] = ()          # empty = any plan in applies_to
    min_amount_inr: int = 0
    expires_on: Optional[str] = None        # ISO date, inclusive
    first_purchase_only: bool = False
    requires_verification: bool = False
    # An announced offer that is not yet redeemable. Listed so the modal can
    # show what is coming without accepting a code that would do nothing.
    active: bool = True
    note: str = ""


PROMOTIONS: Tuple[Promotion, ...] = (
    Promotion(
        code="WELCOME20", kind=PERCENTAGE, value=20,
        description="20% off your first purchase",
        applies_to=(ONE_TIME,), min_amount_inr=99, first_purchase_only=True,
    ),
    Promotion(
        code="STUDENT50", kind=PERCENTAGE, value=50,
        description="50% off for verified students",
        min_amount_inr=49, requires_verification=True,
        note="Needs a verified student email. Verification is not live yet.",
    ),
    Promotion(
        # Kept at the date it was announced. An expired code has to read as
        # expired; quietly extending it would make every future expiry a lie.
        code="EARLYBIRD", kind=FIXED, value=2000,
        description="₹20 off the Pro or Team pack",
        applies_to=(ONE_TIME,), plan_ids=("pro", "team"),
        expires_on="2025-12-31",
    ),
    Promotion(
        code="REFERRAL", kind=FIXED, value=0,
        description="Refer a founder: you both get 10 tokens",
        active=False,
        note="Coming with payments. Granting tokens per referral needs abuse "
             "controls first, or a throwaway address mints free tokens.",
    ),
)

PROMOTIONS_BY_CODE = {p.code: p for p in PROMOTIONS}


@dataclass(frozen=True)
class PromoResult:
    promotion: Optional[Promotion]
    discount_minor: int
    error: str = ""


def apply_promotion(
    code: Optional[str],
    plan: Plan,
    currency: Currency,
    list_minor: int,
    *,
    has_purchased_before: bool = False,
    today: Optional[date] = None,
) -> PromoResult:
    """Validate a code against this plan and return the discount in minor units.

    Every rejection returns a reason the UI can show verbatim. The caller never
    decides whether a code is valid — that is the point of doing it here.
    """
    entered = (code or "").strip().upper()
    if not entered:
        return PromoResult(None, 0)

    promo = PROMOTIONS_BY_CODE.get(entered)
    if not promo or not promo.active:
        return PromoResult(None, 0, "That code is not valid.")

    if promo.expires_on:
        expiry = date.fromisoformat(promo.expires_on)
        if (today or date.today()) > expiry:
            return PromoResult(None, 0, f"That code expired on {expiry:%d %b %Y}.")

    if plan.kind not in promo.applies_to:
        label = "one-time packs" if promo.applies_to == (ONE_TIME,) else "subscriptions"
        return PromoResult(None, 0, f"That code only applies to {label}.")

    if promo.plan_ids and plan.id not in promo.plan_ids:
        names = ", ".join(PLANS_BY_ID[pid].name for pid in promo.plan_ids if pid in PLANS_BY_ID)
        return PromoResult(None, 0, f"That code only applies to: {names}.")

    if promo.first_purchase_only and has_purchased_before:
        return PromoResult(None, 0, "That code is for a first purchase only.")

    if promo.requires_verification:
        return PromoResult(None, 0, promo.note or "This code needs verification first.")

    # Thresholds are published in INR. Comparing them against a USD total would
    # silently apply an INR floor to a different currency.
    if promo.min_amount_inr:
        if currency.code != DEFAULT_CURRENCY:
            return PromoResult(None, 0, "That code applies to ₹ pricing only.")
        if list_minor < promo.min_amount_inr * 100:
            return PromoResult(None, 0, f"Spend at least ₹{promo.min_amount_inr} to use that code.")

    if promo.kind == PERCENTAGE:
        discount = list_minor * promo.value // 100
    else:
        if currency.code != DEFAULT_CURRENCY:
            return PromoResult(None, 0, "That code applies to ₹ pricing only.")
        discount = promo.value

    # Never let a discount exceed the price and turn into a credit.
    return PromoResult(promo, min(discount, list_minor))


def public_promotions() -> List[Promotion]:
    """Codes worth advertising in the UI. Expired ones are dropped so the modal
    never invites someone to type a code that cannot work."""
    today = date.today()
    out = []
    for promo in PROMOTIONS:
        if promo.expires_on and today > date.fromisoformat(promo.expires_on):
            continue
        out.append(promo)
    return out
