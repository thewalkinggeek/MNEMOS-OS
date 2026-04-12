import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mnemos.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

def init_db():
    """Initializes the MÍMIR-DB using the provided schema.sql."""
    if not os.path.exists(SCHEMA_PATH):
        print(f"Error: {SCHEMA_PATH} not found.")
        return

    try:
        # Connect to SQLite (creates the file if it doesn't exist)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Read and execute the schema, explicitly using UTF-8 to avoid encoding errors
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_script = f.read()
        
        cursor.executescript(schema_script)
        conn.commit()
        
        print(f"✅ MÍMIR-DB initialized successfully as '{DB_PATH}'")
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📊 Active Tables: {', '.join(tables)}")

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    init_db()
