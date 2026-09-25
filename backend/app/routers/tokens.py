from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TokenBalance, TokenTransaction
from app.schemas import TokenBalanceResponse, PackageResponse, PurchaseRequest, PurchaseResponse
from app.auth import get_current_user, require_role, ensure_token_balance
from app.config import get_settings

router = APIRouter(prefix="/tokens", tags=["tokens"])
settings = get_settings()

PACKAGES = [
    {"id": "starter", "name": "Starter", "price_rs": 49, "tokens": 20},
    {"id": "pro", "name": "Pro", "price_rs": 99, "tokens": 50},
    {"id": "enterprise", "name": "Enterprise", "price_rs": 179, "tokens": 100},
]

@router.get("/balance", response_model=TokenBalanceResponse)
def get_balance(db: Session = Depends(get_db), user = Depends(get_current_user)):
    balance = ensure_token_balance(db, user.id)
    return TokenBalanceResponse(balance=balance.balance)

@router.get("/packages", response_model=list[PackageResponse])
def list_packages():
    return [PackageResponse(**p) for p in PACKAGES]

@router.post("/purchase", response_model=PurchaseResponse)
def purchase_package(request: PurchaseRequest, db: Session = Depends(get_db), user = Depends(require_role(["solver"]))):
    pkg = next((p for p in PACKAGES if p["id"] == request.package_id), None)
    if not pkg:
        raise HTTPException(status_code=400, detail="Invalid package")
    
    idempotency_key = f"purchase_{user.id}_{request.package_id}"
    existing = db.query(TokenTransaction).filter(TokenTransaction.idempotency_key == idempotency_key).first()
    if existing:
        balance = ensure_token_balance(db, user.id)
        return PurchaseResponse(balance=balance.balance, transaction_id=existing.id)
    
    balance = ensure_token_balance(db, user.id)
    balance.balance += pkg["tokens"]
    
    txn = TokenTransaction(
        user_id=user.id,
        amount=pkg["tokens"],
        type="credit",
        reason=f"package_{request.package_id}",
        idempotency_key=idempotency_key
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    db.refresh(balance)
    
    return PurchaseResponse(balance=balance.balance, transaction_id=txn.id)