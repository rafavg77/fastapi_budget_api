from sqlalchemy.orm import Session
from ..models.models import Card
from ..schemas.schemas import CardCreate

def get_card(db: Session, card_id: int):
    return db.query(Card).filter(Card.id == card_id).first()

def get_user_cards(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Card).filter(Card.owner_id == user_id).offset(skip).limit(limit).all()

def create_card(db: Session, card: CardCreate, user_id: int):
    db_card = Card(**card.dict(), owner_id=user_id)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

def delete_card(db: Session, card_id: int):
    card = db.query(Card).filter(Card.id == card_id).first()
    if card:
        db.delete(card)
        db.commit()
    return card