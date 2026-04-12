import sqlite3
import os

DB_NAME = "mnemos.db"
SCHEMA_FILE = "schema.sql"

def init_db():
    """Initializes the MÍMIR-DB using the provided schema.sql."""
    if not os.path.exists(SCHEMA_FILE):
        print(f"Error: {SCHEMA_FILE} not found.")
        return

    try:
        # Connect to SQLite (creates the file if it doesn't exist)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Read and execute the schema, explicitly using UTF-8 to avoid encoding errors
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            schema_script = f.read()
        
        cursor.executescript(schema_script)
        conn.commit()
        
        print(f"✅ MÍMIR-DB initialized successfully as '{DB_NAME}'")
        print(f"📍 Location: {os.path.abspath(DB_NAME)}")
        
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
