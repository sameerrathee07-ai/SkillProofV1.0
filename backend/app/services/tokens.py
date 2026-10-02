from sqlalchemy.orm import Session
from app.models import TokenBalance, TokenTransaction, TransactionType
from app.schemas import TokenPackage, PurchaseRequest, PurchaseResponse, TokenBalanceResponse
from app.core.config import settings
import uuid


PACKAGES = [
    TokenPackage(id="starter", name="Starter Pack", price_rs=29, tokens=10),
    TokenPackage(id="pro", name="Pro Pack", price_rs=59, tokens=20),
    TokenPackage(id="expert", name="Expert Pack", price_rs=99, tokens=50),
    TokenPackage(id="enterprise", name="Enterprise Pack", price_rs=179, tokens=100),
]


def get_balance(db: Session, user_id: int) -> TokenBalanceResponse:
    balance = db.query(TokenBalance).filter(TokenBalance.user_id == user_id).first()
    if not balance:
        balance = TokenBalance(user_id=user_id, balance=settings.SIGNUP_TOKENS)
        db.add(balance)
        db.commit()
        db.refresh(balance)
    return TokenBalanceResponse(balance=balance.balance)


def get_packages() -> List[TokenPackage]:
    return PACKAGES


def debit_tokens(db: Session, user_id: int, amount: int, reason: str, idempotency_key: str) -> bool:
    existing = db.query(TokenTransaction).filter(
        TokenTransaction.idempotency_key == idempotency_key
    ).first()
    if existing:
        return True
    
    balance = db.query(TokenBalance).filter(TokenBalance.user_id == user_id).first()
    if not balance or balance.balance < amount:
        return False
    
    balance.balance -= amount
    transaction = TokenTransaction(
        user_id=user_id,
        amount=amount,
        type=TransactionType.DEBIT,
        reason=reason,
        idempotency_key=idempotency_key,
    )
    db.add(transaction)
    db.commit()
    return True


def credit_tokens(db: Session, user_id: int, amount: int, reason: str, idempotency_key: str) -> bool:
    existing = db.query(TokenTransaction).filter(
        TokenTransaction.idempotency_key == idempotency_key
    ).first()
    if existing:
        return True
    
    balance = db.query(TokenBalance).filter(TokenBalance.user_id == user_id).first()
    if not balance:
        balance = TokenBalance(user_id=user_id, balance=0)
        db.add(balance)
        db.flush()
    
    balance.balance += amount
    transaction = TokenTransaction(
        user_id=user_id,
        amount=amount,
        type=TransactionType.CREDIT,
        reason=reason,
        idempotency_key=idempotency_key,
    )
    db.add(transaction)
    db.commit()
    return True


def purchase_package(db: Session, user_id: int, req: PurchaseRequest) -> PurchaseResponse:
    package = next((p for p in PACKAGES if p.id == req.package_id), None)
    if not package:
        return PurchaseResponse(success=False, new_balance=0, tokens_added=0)
    
    success = credit_tokens(db, user_id, package.tokens, f"purchase_{package.id}", req.idempotency_key)
    if not success:
        return PurchaseResponse(success=False, new_balance=0, tokens_added=0)
    
    balance = db.query(TokenBalance).filter(TokenBalance.user_id == user_id).first()
    return PurchaseResponse(success=True, new_balance=balance.balance, tokens_added=package.tokens)