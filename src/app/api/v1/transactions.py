from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...crud import transaction as transaction_crud
from ...crud import card as card_crud
from ...schemas import schemas
from ...dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/cards/{card_id}/transactions/", response_model=schemas.Transaction)
def create_transaction(
    card_id: int,
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    card = card_crud.get_card(db, card_id=card_id)
    if card is None or card.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    return transaction_crud.create_transaction(
        db=db, transaction=transaction, card_id=card_id
    )

@router.get("/cards/{card_id}/transactions/", response_model=List[schemas.Transaction])
def read_transactions(
    card_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    card = card_crud.get_card(db, card_id=card_id)
    if card is None or card.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    return transaction_crud.get_card_transactions(
        db, card_id=card_id, skip=skip, limit=limit
    )

@router.delete("/transactions/{transaction_id}", response_model=schemas.Transaction)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    transaction = transaction_crud.get_transaction(db, transaction_id=transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    card = card_crud.get_card(db, card_id=transaction.card_id)
    if card.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return transaction_crud.delete_transaction(db=db, transaction_id=transaction_id)