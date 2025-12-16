"""Quick script to check database schema"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "instance" / "mindscope_ai_flask.db"

if not DB_PATH.exists():
    print(f"Database not found at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Check User table columns
cursor.execute("PRAGMA table_info(user)")
columns = [row[1] for row in cursor.fetchall()]
print("User table columns:", columns)

# Check required columns
required = ['high_risk_flag', 'high_risk_reason', 'high_risk_updated_at']
missing = [c for c in required if c not in columns]
if missing:
    print(f"❌ Missing columns: {missing}")
else:
    print("✅ All required User columns present")

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("\nTables:", tables)

required_tables = ['resource', 'admin_audit_log']
missing_tables = [t for t in required_tables if t not in tables]
if missing_tables:
    print(f"❌ Missing tables: {missing_tables}")
else:
    print("✅ All required tables present")

conn.close()

