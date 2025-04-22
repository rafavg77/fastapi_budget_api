from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..models.models import User
from ..schemas.schemas import UserCreate
from ..core.security import get_password_hash

logger = logging.getLogger(__name__)

def get_user(db: Session, user_id: int) -> User | None:
    try:
        return db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user: {str(e)}", extra={"security": True})
        raise

def get_user_by_email(db: Session, email: str) -> User | None:
    try:
        return db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_by_email: {str(e)}", extra={"security": True})
        raise

def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_users: {str(e)}", extra={"security": True})
        raise

def create_user(db: Session, user: UserCreate) -> User:
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Created new user: {user.email}", extra={"security": True})
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in create_user: {str(e)}", extra={"security": True})
        raise

def update_user(db: Session, user_id: int, user_update: dict) -> User | None:
    try:
        db_user = get_user(db, user_id)
        if db_user is None:
            return None
        
        for key, value in user_update.items():
            if key == "password":
                setattr(db_user, "hashed_password", get_password_hash(value))
            else:
                setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        logger.info(f"Updated user: {db_user.email}", extra={"security": True})
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in update_user: {str(e)}", extra={"security": True})
        raise

def delete_user(db: Session, user_id: int) -> bool:
    try:
        db_user = get_user(db, user_id)
        if db_user is None:
            return False
        
        db.delete(db_user)
        db.commit()
        logger.info(f"Deleted user: {db_user.email}", extra={"security": True})
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in delete_user: {str(e)}", extra={"security": True})
        raise