from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./budget.db"
)

# Create SQLite engine with foreign key support
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize database with all tables."""
    Base.metadata.create_all(bind=engine)

def get_test_db() -> Session:
    """Get test database session."""
    try:
        # Create test database and tables
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        yield db
    finally:
        # Clean up
        Base.metadata.drop_all(bind=engine)
        db.close()