import os


def check_env_file():
    """Check and fix .env file encoding issues"""
    env_path = ".env"

    print("Checking .env file...")

    if not os.path.exists(env_path):
        print("Error: .env file not found")
        return False

    try:
        # Try to read with utf-8
        with open(env_path, encoding="utf-8") as f:
            content = f.read()
            print("Successfully read .env file (UTF-8)")
            print("\nCurrent content:")
            print("-" * 40)
            print(content)
            print("-" * 40)
            return True

    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}")
        print("\nTrying to fix encoding...")

        # Try different encodings
        encodings = ["utf-8-sig", "latin-1", "cp1251", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                with open(env_path, encoding=encoding) as f:
                    content = f.read()
                    print(f"\nSuccessfully read with {encoding} encoding")

                    # Write back with UTF-8
                    with open(env_path, "w", encoding="utf-8") as f_out:
                        f_out.write(content)

                    print("File converted to UTF-8")
                    print("\nFixed content:")
                    print("-" * 40)
                    print(content)
                    print("-" * 40)
                    return True

            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error with {encoding}: {e}")

    print("\nCould not fix encoding automatically")
    return False

def create_new_env():
    """Create a fresh .env file"""
    print("\nCreating new .env file...")

    content = """DATABASE_URL=postgresql://postgres:your_password_here@localhost:5432/knowledge_base
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production
"""

    with open(".env", "w", encoding="utf-8") as f:
        f.write(content)

    print("New .env file created")
    print("\nIMPORTANT: Update the password in .env file")
    print("Change 'your_password_here' to your actual PostgreSQL password")

    return True

def check_postgres_connection():
    """Test PostgreSQL connection"""
    print("\n" + "=" * 50)
    print("Testing PostgreSQL connection...")

    try:
        import psycopg2

        # Read DATABASE_URL from .env
        with open(".env", encoding="utf-8") as f:
            lines = f.readlines()

        db_url = None
        for line in lines:
            if line.startswith("DATABASE_URL="):
                db_url = line.strip().split("=", 1)[1]
                break

        if not db_url:
            print("DATABASE_URL not found in .env file")
            return False

        print(f"Testing connection to: {db_url}")

        # Parse URL (simplified)
        if db_url.startswith("postgresql://"):
            url_parts = db_url.replace("postgresql://", "").split("/")
            credentials_host = url_parts[0]

            if "@" in credentials_host:
                credentials, host_port = credentials_host.split("@")
                user_pass = credentials.split(":")
                username = user_pass[0]
                password = user_pass[1] if len(user_pass) > 1 else ""
            else:
                host_port = credentials_host
                username = "postgres"
                password = ""

            if ":" in host_port:
                host, port = host_port.split(":")
            else:
                host = host_port
                port = "5432"

            database = url_parts[1] if len(url_parts) > 1 else "postgres"

        # Test connection
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]

        print(f"Success! PostgreSQL version: {version}")

        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"Connected to database: {db_name}")

        cursor.close()
        conn.close()
        return True

    except ImportError:
        print("psycopg2 not installed")
        return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def main():
    print("=" * 50)
    print(".env File Fix Utility")
    print("=" * 50)

    # Step 1: Check current .env file
    if not check_env_file():
        print("\nCreating new .env file...")
        create_new_env()

    # Step 2: Update password if needed
    print("\n" + "=" * 50)
    print("IMPORTANT: Make sure .env file has correct password")
    print("Open .env file and update:")
    print("DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/knowledge_base")

    input("\nPress Enter after updating password...")

    # Step 3: Test PostgreSQL connection
    if check_postgres_connection():
        print("\n" + "=" * 50)
        print("SUCCESS: PostgreSQL connection works!")
        print("\nNext command:")
        print("python scripts/init_db.py")
    else:
        print("\n" + "=" * 50)
        print("ERROR: Could not connect to PostgreSQL")
        print("\nTroubleshooting:")
        print("1. Check password in .env file")
        print("2. Make sure PostgreSQL service is running")
        print("3. Verify database 'knowledge_base' exists")

if __name__ == "__main__":
    main()
