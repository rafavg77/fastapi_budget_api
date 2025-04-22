from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...crud import card as card_crud
from ...schemas import schemas
from ...dependencies import get_db, get_current_user

router = APIRouter()

def mask_card_number(card_number: str) -> str:
    """Mask all but the last 4 digits of card number"""
    if not card_number:
        return ""
    return "*" * (len(card_number) - 4) + card_number[-4:]

def mask_card_response(card: schemas.Card) -> schemas.Card:
    """Mask sensitive data in card response"""
    card.card_number = mask_card_number(card.card_number)
    return card

@router.post("/cards/", response_model=schemas.Card)
def create_card(
    card: schemas.CardCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_card = card_crud.create_card(db=db, card=card, user_id=current_user.id)
    return mask_card_response(schemas.Card.from_orm(db_card))

@router.get("/cards/", response_model=List[schemas.Card])
def read_cards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    cards = card_crud.get_user_cards(db, user_id=current_user.id, skip=skip, limit=limit)
    return [mask_card_response(schemas.Card.from_orm(card)) for card in cards]

@router.get("/cards/{card_id}", response_model=schemas.Card)
def read_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_card = card_crud.get_card(db, card_id=card_id)
    if db_card is None or db_card.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    return mask_card_response(schemas.Card.from_orm(db_card))

@router.delete("/cards/{card_id}", response_model=schemas.Card)
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_card = card_crud.get_card(db, card_id=card_id)
    if db_card is None or db_card.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Card not found")
    card_crud.delete_card(db=db, card_id=card_id)
    return {"message": "Card deleted successfully"}