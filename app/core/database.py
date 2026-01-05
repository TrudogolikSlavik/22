from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

# Create PostgreSQL engine
engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
