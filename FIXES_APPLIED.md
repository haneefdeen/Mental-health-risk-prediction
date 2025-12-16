# Database Migration Fixes Applied

## Problem
The app was failing to start with error:
```
sqlite3.OperationalError: no such column: user.high_risk_flag
```

This occurred because new columns were added to the User model, but the existing database didn't have these columns.

## Solution Applied

### 1. Created Migration Script
- **File**: `backend/migrate_add_columns.py`
- Adds missing columns to existing database:
  - `user.high_risk_flag` (BOOLEAN)
  - `user.high_risk_reason` (VARCHAR(500))
  - `user.high_risk_updated_at` (DATETIME)
- Creates new tables if they don't exist:
  - `resource` table
  - `admin_audit_log` table

### 2. Added Auto-Migration to App
- **File**: `mindscope_flask/app.py`
- Added `_run_migrations()` function that automatically:
  - Checks for missing columns
  - Adds them if missing
  - Creates new tables if they don't exist
- Runs automatically on app startup before `db.create_all()`

### 3. Verified Database Schema
- **File**: `backend/check_db.py`
- Utility script to verify all required columns and tables exist

## Verification

✅ Database has all required columns:
- `high_risk_flag`
- `high_risk_reason`
- `high_risk_updated_at`

✅ All required tables exist:
- `resource`
- `admin_audit_log`

✅ App starts successfully
✅ Server responds on http://localhost:5000

## How to Run

1. **Activate virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Run the app**:
   ```powershell
   python -m mindscope_flask.app
   ```

3. **Access the app**:
   - Main app: http://localhost:5000
   - Admin dashboard: http://localhost:5000/admin
   - API status: http://localhost:5000/api/system/status

## Notes

- The migration runs automatically on startup, so you don't need to run it manually
- If you need to manually run migrations, use:
  ```powershell
  python backend/migrate_add_columns.py
  ```
- The warnings about DistilBERT and ResNet weights are normal and don't affect functionality

