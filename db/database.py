import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tracecredit.db")

engine = create_engine(
    DATABASE_URL, 
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def get_database_url() -> str:
    """Get the current database URL."""
    return DATABASE_URL

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()