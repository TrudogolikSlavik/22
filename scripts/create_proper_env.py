
def create_proper_env():
    """Create properly formatted .env file"""
    print("Creating proper .env file...")

    # Your actual password
    password = "Vyacheslav2006/"

    content = f"""DATABASE_URL=postgresql://postgres:{password}@localhost:5432/knowledge_base
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production
"""

    with open(".env", "w", encoding="utf-8") as f:
        f.write(content)

    print(".env file created successfully")
    print("\nContent:")
    print("-" * 40)
    print(content)
    print("-" * 40)

    return True

def verify_database_exists():
    """Verify knowledge_base database exists"""
    print("\nVerifying database...")

    try:
        import psycopg2

        # First connect to postgres database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="Vyacheslav2006/",
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if knowledge_base exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='knowledge_base'")

        if cursor.fetchone():
            print("Database 'knowledge_base' exists")

            # Try to connect to it
            try:
                cursor.close()
                conn.close()

                conn = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    user="postgres",
                    password="Vyacheslav2006/",
                    database="knowledge_base"
                )

                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print("Successfully connected to knowledge_base")
                print(f"PostgreSQL version: {version}")

                cursor.close()
                conn.close()
                return True

            except Exception as e:
                print(f"Could not connect to knowledge_base: {e}")
                return False
        else:
            print("Database 'knowledge_base' does not exist")
            print("Creating it now...")

            cursor.execute("CREATE DATABASE knowledge_base")
            print("Database 'knowledge_base' created")

            cursor.close()
            conn.close()
            return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def test_connection():
    """Test connection using DATABASE_URL from .env"""
    print("\nTesting connection from .env file...")

    try:
        import psycopg2

        # Read DATABASE_URL from .env
        with open(".env", encoding="utf-8") as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    db_url = line.strip().split("=", 1)[1]
                    break

        print(f"Connecting to: {db_url}")

        # Connect using the URL
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]

        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]

        print("Success!")
        print(f"PostgreSQL version: {version}")
        print(f"Connected to database: {db_name}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Connection error: {e}")
        return False

def main():
    print("=" * 50)
    print("Database Configuration Setup")
    print("=" * 50)

    # Step 1: Create proper .env file
    print("\n1. Creating .env file...")
    create_proper_env()

    # Step 2: Verify database exists
    print("\n2. Verifying database...")
    if not verify_database_exists():
        print("Database verification failed")
        return

    # Step 3: Test connection
    print("\n3. Testing connection...")
    if test_connection():
        print("\n" + "=" * 50)
        print("SUCCESS: Everything is configured correctly!")
        print("\nNext command:")
        print("python scripts/init_db.py")
    else:
        print("\n" + "=" * 50)
        print("ERROR: Configuration failed")

if __name__ == "__main__":
    main()
