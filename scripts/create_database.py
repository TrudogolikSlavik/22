import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import psycopg2

from app.core.config import settings

print("Creating knowledge_base database...")

try:
    # Extract connection parameters from DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    db_url = settings.DATABASE_URL

    # Parse the URL (simplified parsing)
    if db_url.startswith("postgresql://"):
        # Remove protocol
        url_parts = db_url.replace("postgresql://", "").split("/")
        credentials_host = url_parts[0]
        database_name = url_parts[1] if len(url_parts) > 1 else "postgres"

        # Split credentials and host
        if "@" in credentials_host:
            credentials, host_port = credentials_host.split("@")
            user_pass = credentials.split(":")
            username = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
        else:
            host_port = credentials_host
            username = "postgres"
            password = ""

        # Split host and port
        if ":" in host_port:
            host, port = host_port.split(":")
        else:
            host = host_port
            port = "5432"

    # Connect to PostgreSQL server (to postgres database)
    print(f"Connecting to PostgreSQL at {host}:{port}...")
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        database="postgres"  # Connect to default postgres database
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Check if database already exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='knowledge_base'")

    if cursor.fetchone():
        print("Database 'knowledge_base' already exists")
    else:
        # Create database
        cursor.execute("CREATE DATABASE knowledge_base")
        print("Database 'knowledge_base' created successfully")

    # Verify database creation
    cursor.execute("SELECT datname FROM pg_database WHERE datname='knowledge_base'")
    result = cursor.fetchone()

    if result:
        print(f"Verified: Database '{result[0]}' exists")

    cursor.close()
    conn.close()

    print("\nNext steps:")
    print("1. Update your .env file with:")
    print(f"   DATABASE_URL=postgresql://{username}:{password}@{host}:{port}/knowledge_base")
    print("2. Run: python scripts/init_db.py")

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you are running from the project root directory")
except psycopg2.Error as e:
    print(f"Database error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure PostgreSQL service is running")
    print("2. Check your password in .env file")
    print("3. Verify connection parameters")
except Exception as e:
    print(f"Error: {e}")
