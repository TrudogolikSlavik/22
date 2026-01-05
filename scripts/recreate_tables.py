import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine
from app.models.base import Base


def recreate_tables():
    """Recreate all tables with new fields"""
    print("WARNING: This will DROP ALL TABLES!")
    print("Type 'YES' to continue: ", end="")
    confirmation = input().strip()

    if confirmation != "YES":
        print("Operation cancelled")
        return False

    try:
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)

        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)

        # Check created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print("All tables recreated successfully!")
        print(f"Tables: {tables}")

        return True
    except Exception as e:
        print(f"Error recreating tables: {e}")
        return False


if __name__ == "__main__":
    try:
        success = recreate_tables()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
