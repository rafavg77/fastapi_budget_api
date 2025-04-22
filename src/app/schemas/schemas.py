from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class TransactionBase(BaseModel):
    amount: float
    description: str
    type: str

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    date: datetime
    card_id: int

    class Config:
        orm_mode = True

class CardBase(BaseModel):
    card_number: str
    card_name: str
    bank_name: str

class CardCreate(CardBase):
    pass

class Card(CardBase):
    id: int
    owner_id: int
    transactions: List[Transaction] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    cards: List[Card] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None