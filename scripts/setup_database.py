import sys

import psycopg2

print("Database setup script")

def create_database():
    """Create knowledge_base database"""
    # Your PostgreSQL password
    password = "Vyacheslav2006/"

    try:
        # Connect to PostgreSQL server
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password=password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print("Checking if database exists...")
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='knowledge_base'")

        if cursor.fetchone():
            print("Database 'knowledge_base' already exists")
        else:
            print("Creating database 'knowledge_base'...")
            cursor.execute("CREATE DATABASE knowledge_base")
            print("Database created successfully")

        cursor.close()
        conn.close()

        return True

    except psycopg2.OperationalError as e:
        print(f"Connection error: {e}")
        print("\nPossible solutions:")
        print("1. Wrong password - update the password in this script")
        print("2. PostgreSQL service not running")
        print("3. Check firewall settings")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def update_env_file():
    """Update .env file with database URL"""
    try:
        # Read current .env file
        with open(".env", encoding="utf-8") as f:
            lines = f.readlines()

        # Update DATABASE_URL line
        updated_lines = []
        for line in lines:
            if line.startswith("DATABASE_URL="):
                updated_lines.append("DATABASE_URL=postgresql://postgres:your_password_here@localhost:5432/knowledge_base\n")
            else:
                updated_lines.append(line)

        # Write back
        with open(".env", "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        print("Updated .env file with new DATABASE_URL")

    except FileNotFoundError:
        # Create new .env file
        with open(".env", "w", encoding="utf-8") as f:
            f.write("DATABASE_URL=postgresql://postgres:your_password_here@localhost:5432/knowledge_base\n")
            f.write("DEBUG=true\n")
            f.write("SECRET_KEY=your-super-secret-key-change-in-production\n")

        print("Created new .env file")

def main():
    print("=" * 50)
    print("Knowledge Base Database Setup")
    print("=" * 50)

    # Step 1: Update password in this file
    print("\nIMPORTANT: Update the password in this script (line 8)")
    print("Current: password = \"your_password_here\"")
    print("Change to: password = \"your_actual_password\"")

    input("\nPress Enter after updating the password...")

    # Step 2: Create database
    print("\n" + "-" * 50)
    print("Creating database...")
    if not create_database():
        print("Failed to create database")
        sys.exit(1)

    # Step 3: Update .env file
    print("\n" + "-" * 50)
    print("Updating configuration...")
    update_env_file()

    print("\n" + "=" * 50)
    print("Setup completed!")
    print("\nNext command:")
    print("python scripts/init_db.py")

if __name__ == "__main__":
    main()
