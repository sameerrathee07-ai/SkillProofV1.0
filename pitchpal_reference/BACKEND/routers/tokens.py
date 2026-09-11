from datetime import datetime, time, timedelta
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import models
import payments
import schemas
from auth import get_current_user
from database import get_db
from models import utcnow

router = APIRouter(prefix="/tokens", tags=["tokens"])

# SECURITY: /purchase credits tokens with no payment verification — there is no
# gateway wired up yet. Left open, any signed-in user could mint unlimited tokens
# by calling it in a loop. It stays disabled unless a developer explicitly opts in
# for local testing, and must remain off in any deployed environment until a real
# provider webhook confirms payment before crediting.
ALLOW_UNVERIFIED_PURCHASE = os.getenv("ALLOW_UNVERIFIED_PURCHASE", "false").lower() in ("1", "true", "yes")


# ── Serialisation helpers ─────────────────────────────────

def _plan_out(plan: payments.Plan, currency: payments.Currency) -> schemas.PlanOut:
    minor = plan.price_minor(currency)
    return schemas.PlanOut(
        id=plan.id,
        name=plan.name,
        kind=plan.kind,
        tokens=plan.tokens,
        tokens_per_month=plan.tokens_per_month,
        interval=plan.interval,
        description=plan.description,
        badge=plan.badge,
        popular=plan.popular,
        amount_minor=minor,
        amount_display=payments.format_amount(minor, currency),
        pitches=plan.tokens // payments.TOKENS_PER_PITCH,
    )


def _currency_out(currency: payments.Currency) -> schemas.CurrencyOut:
    return schemas.CurrencyOut(
        code=currency.code, symbol=currency.symbol, decimals=currency.decimals
    )


def _method_out(method: payments.PaymentMethod) -> schemas.PaymentMethodOut:
    return schemas.PaymentMethodOut(
        id=method.id,
        name=method.name,
        description=method.description,
        icon=method.icon,
        min_amount_inr=method.min_amount_inr,
    )


def _has_purchased_before(db: Session, user_id: int) -> bool:
    """Whether this account has ever been credited by a purchase. Drives the
    first-purchase-only promo, and has to be a server check — the client has no
    way to prove it, and every reason to claim it."""
    return db.query(models.TokenTransaction.id).filter(
        models.TokenTransaction.user_id == user_id,
        models.TokenTransaction.type == "credit",
        models.TokenTransaction.reason.like("purchase_%"),
    ).first() is not None


# ── Catalogue ─────────────────────────────────────────────

@router.get("/catalog", response_model=schemas.CatalogOut)
def catalog(currency: Optional[str] = Query(None, description="ISO code, e.g. INR or USD")):
    """Public: every plan, method and live promo in one request.

    Public because the pricing page shows it before sign-in, and because
    nothing here is per-user — the per-user parts live in /quote.
    """
    cur = payments.resolve_currency(currency)
    return schemas.CatalogOut(
        currency=_currency_out(cur),
        currencies=[_currency_out(c) for c in payments.CURRENCIES.values()],
        one_time=[_plan_out(p, cur) for p in payments.plans_of_kind(payments.ONE_TIME)],
        subscriptions=[_plan_out(p, cur) for p in payments.plans_of_kind(payments.SUBSCRIPTION)],
        payment_methods=[_method_out(m) for m in payments.PAYMENT_METHODS],
        promotions=[
            schemas.PromotionOut(
                code=p.code,
                description=p.description,
                active=p.active,
                note=p.note,
                expires_on=p.expires_on,
            )
            for p in payments.public_promotions()
        ],
        tokens_per_message=payments.TOKENS_PER_MESSAGE,
        tokens_per_pitch=payments.TOKENS_PER_PITCH,
        emi_tenures=list(payments.EMI_TENURES),
    )


@router.post("/quote", response_model=schemas.QuoteOut)
def quote(
    payload: schemas.QuoteRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Price one plan for this user, with any promo code applied.

    The only place a total is computed. The client sends the plan and the code
    and renders what comes back; it never subtracts a discount itself.
    """
    plan = payments.get_plan(payload.plan)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown plan: {payload.plan}",
        )

    cur = payments.resolve_currency(payload.currency)
    list_minor = plan.price_minor(cur)

    result = payments.apply_promotion(
        payload.promo_code,
        plan,
        cur,
        list_minor,
        has_purchased_before=_has_purchased_before(db, user.id),
        today=utcnow().date(),
    )

    total_minor = list_minor - result.discount_minor
    balance = user.token_balance.balance if user.token_balance else 0
    # What the balance *would* be. Advisory arithmetic for the summary line — the
    # real credit only ever happens in /purchase, against a confirmed payment.
    balance_after = balance + plan.tokens

    return schemas.QuoteOut(
        plan=plan.id,
        tokens=plan.tokens,
        currency=_currency_out(cur),
        list_minor=list_minor,
        list_display=payments.format_amount(list_minor, cur),
        discount_minor=result.discount_minor,
        discount_display=payments.format_amount(result.discount_minor, cur),
        total_minor=total_minor,
        total_display=payments.format_amount(total_minor, cur),
        promo_code=result.promotion.code if result.promotion else None,
        promo_description=result.promotion.description if result.promotion else None,
        promo_error=result.error or None,
        eligible_methods=[_method_out(m) for m in payments.eligible_methods(total_minor, cur)],
        balance_after=balance_after,
        pitches_after=balance_after // payments.TOKENS_PER_PITCH,
    )


@router.get("/packages", response_model=List[schemas.PackageOut])
def list_packages():
    """The one-time packs in the original flat shape, cheapest first.

    Kept alongside /catalog for the marketing pricing grid, which needs three
    fields and no currency handling.
    """
    return [
        schemas.PackageOut(
            id=plan.id,
            tokens=plan.tokens,
            price_inr=plan.prices[payments.DEFAULT_CURRENCY] // 100,
            popular=plan.popular,
        )
        for plan in payments.plans_of_kind(payments.ONE_TIME)
    ]


# ── Purchase (disabled until a gateway confirms payment) ───

@router.post("/purchase", response_model=schemas.PurchaseResponse)
def purchase_tokens(
    payload: schemas.PurchaseRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = payments.get_plan(payload.package)
    if not plan or plan.kind != payments.ONE_TIME:
        valid = ", ".join(p.id for p in payments.plans_of_kind(payments.ONE_TIME))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid package. Choose from: {valid}",
        )

    # Refuse to credit tokens nobody has paid for.
    if not ALLOW_UNVERIFIED_PURCHASE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Payments are not available yet — token purchases are disabled.",
        )

    balance = user.token_balance
    if not balance:
        balance = models.TokenBalance(user_id=user.id, balance=0)
        db.add(balance)
        db.flush()

    balance.balance += plan.tokens
    db.add(models.TokenTransaction(
        user_id=user.id,
        amount=plan.tokens,
        type="credit",
        reason=f"purchase_{plan.id}",
    ))
    db.commit()

    return schemas.PurchaseResponse(
        success=True,
        tokens_added=plan.tokens,
        new_balance=balance.balance,
        message=f"Added {plan.tokens} tokens ({plan.name} pack)",
    )


@router.get("/usage", response_model=List[schemas.UsageDay])
def token_usage(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tokens spent per day over the last 7 days, oldest first.

    Days with no activity are returned as zero so the chart keeps a stable
    7-column shape instead of collapsing.
    """
    today = utcnow().date()
    start = today - timedelta(days=6)
    # Compare against a real datetime; created_at is a DATETIME column and a bare
    # date would rely on string-prefix luck in SQLite.
    start_dt = datetime.combine(start, time.min)

    debits = db.query(models.TokenTransaction).filter(
        models.TokenTransaction.user_id == user.id,
        models.TokenTransaction.type == "debit",
        models.TokenTransaction.created_at >= start_dt,
    ).all()

    totals = {}
    for txn in debits:
        if txn.created_at:
            key = txn.created_at.date()
            totals[key] = totals.get(key, 0) + txn.amount

    out = []
    for offset in range(7):
        day = start + timedelta(days=offset)
        out.append(schemas.UsageDay(
            day=day.strftime("%a"),
            date=day.isoformat(),
            tokens=totals.get(day, 0),
        ))
    return out


@router.get("/balance", response_model=schemas.UserOut)
def get_balance(user: models.User = Depends(get_current_user)):
    return schemas.UserOut(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        token_balance=user.token_balance.balance if user.token_balance else 0,
        name=user.name,
        picture=user.picture,
        pdf_downloads=user.pdf_downloads or 0,
    )
