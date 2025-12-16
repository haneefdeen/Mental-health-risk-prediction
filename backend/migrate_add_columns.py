"""
Migration script to add new columns to existing database tables.
Run this once to update the database schema.
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "instance" / "mindscope_ai_flask.db"

def migrate_database():
    """Add new columns to existing tables"""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. It will be created on first run.")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if columns exist and add them if they don't
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add high_risk_flag column
        if 'high_risk_flag' not in columns:
            print("Adding high_risk_flag column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN high_risk_flag BOOLEAN DEFAULT 0")
        
        # Add high_risk_reason column
        if 'high_risk_reason' not in columns:
            print("Adding high_risk_reason column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN high_risk_reason VARCHAR(500)")
        
        # Add high_risk_updated_at column
        if 'high_risk_updated_at' not in columns:
            print("Adding high_risk_updated_at column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN high_risk_updated_at DATETIME")
        
        # Check if Resource table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resource'")
        if not cursor.fetchone():
            print("Creating resource table...")
            cursor.execute("""
                CREATE TABLE resource (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    type VARCHAR(50) NOT NULL,
                    url_or_path VARCHAR(500) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Check if AdminAuditLog table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_audit_log'")
        if not cursor.fetchone():
            print("Creating admin_audit_log table...")
            cursor.execute("""
                CREATE TABLE admin_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (admin_id) REFERENCES user (id)
                )
            """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()

