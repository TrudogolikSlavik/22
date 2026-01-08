
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

# Parse DATABASE_URL or use direct parameters
db_url = settings.DATABASE_URL

# If URL has issues, use direct connection
if "Vyacheslav2006/" in db_url:
    # Use direct connection parameters
    engine = create_engine(
        "postgresql://postgres@localhost:5432/knowledge_base",
        connect_args={
            "password": "Vyacheslav2006/",
            "application_name": "knowledge_base"
        }
    )
else:
    # Use normal URL
    engine = create_engine(db_url)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
