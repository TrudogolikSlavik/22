import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="knowledge_base",
        user="postgres",
        password="password"
    )
    cursor = conn.cursor()

    # Check tables
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()

    print("Connected to PostgreSQL")
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Connection failed: {e}")
