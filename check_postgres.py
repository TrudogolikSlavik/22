import psycopg2

print("Testing PostgreSQL connection...")

YOUR_PASSWORD = "Vyacheslav2006/"

test_connections = [
    {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": YOUR_PASSWORD,
        "database": "postgres"
    },
    {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "",
        "database": "postgres"
    },
]

successful_connection = None

for i, conn_params in enumerate(test_connections, 1):
    try:
        print(f"\nAttempt {i}:")
        print(f"  User: {conn_params['user']}")
        print(f"  Password: {'(specified)' if conn_params['password'] else '(empty)'}")

        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]

        print("Success!")
        print(f"PostgreSQL version: {version}")

        successful_connection = conn_params
        cursor.close()
        conn.close()
        break

    except psycopg2.OperationalError as e:
        print(f"  Connection error: {e}")
    except Exception as e:
        print(f"  Error: {e}")

if successful_connection:
    print("\n" + "="*50)
    print("Working connection parameters:")
    print(f"  Host: {successful_connection['host']}")
    print(f"  Port: {successful_connection['port']}")
    print(f"  User: {successful_connection['user']}")
    print(f"  Password: {'(specified)' if successful_connection['password'] else '(empty)'}")
else:
    print("\nNo successful connections. Please check:")
    print("1. PostgreSQL service is running")
    print("2. Correct password")
    print("3. Firewall settings")
