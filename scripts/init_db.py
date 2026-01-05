import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print("Initializing database tables...")

try:
    from app.core.database import engine
    from app.models.base import Base

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")

    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("\nCreated tables:")
    for table in tables:
        print(f"  - {table}")

    print("\nDatabase initialization completed!")

except ImportError as e:
    print(f"Import error: {e}")
    print("\nMake sure:")
    print("1. You are in the project root directory")
    print("2. Virtual environment is activated")
    print("3. Dependencies are installed")
    sys.exit(1)

except Exception as e:
    print(f"Error creating tables: {e}")
    print("\nPossible issues:")
    print("1. Database connection problem")
    print("2. Wrong credentials in .env file")
    print("3. PostgreSQL service not running")
    sys.exit(1)
