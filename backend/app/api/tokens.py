from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.auth import get_current_user
from app.services.tokens import get_balance, get_packages, purchase_package
from app.schemas import TokenBalanceResponse, TokenPackage, PurchaseRequest, PurchaseResponse
from app.models import User

router = APIRouter(prefix="/tokens", tags=["tokens"])


@router.get("/balance", response_model=TokenBalanceResponse)
def balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_balance(db, current_user.id)


@router.get("/packages", response_model=List[TokenPackage])
def packages():
    return get_packages()


@router.post("/purchase", response_model=PurchaseResponse)
def purchase(
    request: PurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return purchase_package(db, current_user.id, request)