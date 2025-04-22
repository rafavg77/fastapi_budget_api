from sqlalchemy.orm import Session
from ..models.models import Transaction
from ..schemas.schemas import TransactionCreate

def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def get_card_transactions(db: Session, card_id: int, skip: int = 0, limit: int = 100):
    return db.query(Transaction).filter(Transaction.card_id == card_id).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: TransactionCreate, card_id: int):
    db_transaction = Transaction(**transaction.dict(), card_id=card_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction:
        db.delete(transaction)
        db.commit()
    return transaction