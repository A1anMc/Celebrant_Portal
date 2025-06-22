import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_database():
    """Initialize PostgreSQL databases for development and testing."""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "")
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Create development database
        try:
            cur.execute("CREATE DATABASE celebrant_dev")
            print("Successfully created development database: celebrant_dev")
        except psycopg2.Error as e:
            if "already exists" in str(e):
                print("Development database already exists")
            else:
                raise e
        
        # Create test database
        try:
            cur.execute("CREATE DATABASE celebrant_test")
            print("Successfully created test database: celebrant_test")
        except psycopg2.Error as e:
            if "already exists" in str(e):
                print("Test database already exists")
            else:
                raise e
                
        cur.close()
        conn.close()
        
        print("\nDatabase initialization completed successfully!")
        print("\nNext steps:")
        print("1. Create a .env file using .env.example as a template")
        print("2. Set your PostgreSQL credentials in the .env file")
        print("3. Run 'flask db upgrade' to create the tables")
        
    except Exception as e:
        print(f"Error initializing databases: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    init_database() 