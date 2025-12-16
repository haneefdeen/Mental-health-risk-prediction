"""
MindScope AI - Authentication Utilities
JWT-based authentication for user and admin access
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "mindscope-ai-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

# User data storage
USERS_FILE = "data/users.json"
ADMINS_FILE = "data/admins.json"

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def load_users() -> Dict[str, Dict]:
    """Load users from file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}
    return {}

def save_users(users: Dict[str, Dict]):
    """Save users to file"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

def load_admins() -> Dict[str, Dict]:
    """Load admins from file"""
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading admins: {e}")
            return {}
    return {}

def save_admins(admins: Dict[str, Dict]):
    """Save admins to file"""
    os.makedirs(os.path.dirname(ADMINS_FILE), exist_ok=True)
    try:
        with open(ADMINS_FILE, 'w') as f:
            json.dump(admins, f, indent=2)
    except Exception as e:
        print(f"Error saving admins: {e}")

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user"""
    users = load_users()
    if username in users:
        user = users[username]
        if verify_password(password, user["hashed_password"]):
            return {
                "username": username,
                "email": user.get("email", ""),
                "full_name": user.get("full_name", ""),
                "user_type": "user"
            }
    return None

def authenticate_admin(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate an admin"""
    admins = load_admins()
    if username in admins:
        admin = admins[username]
        if verify_password(password, admin["hashed_password"]):
            return {
                "username": username,
                "email": admin.get("email", ""),
                "full_name": admin.get("full_name", ""),
                "user_type": "admin"
            }
    return None

def create_user(username: str, email: str, password: str, full_name: str = "") -> bool:
    """Create a new user"""
    users = load_users()
    if username in users:
        return False
    
    users[username] = {
        "email": email,
        "full_name": full_name,
        "hashed_password": get_password_hash(password),
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    save_users(users)
    return True

def create_admin(username: str, email: str, password: str, full_name: str = "") -> bool:
    """Create a new admin"""
    admins = load_admins()
    if username in admins:
        return False
    
    admins[username] = {
        "email": email,
        "full_name": full_name,
        "hashed_password": get_password_hash(password),
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    save_admins(admins)
    return True

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Check if user exists
        users = load_users()
        admins = load_admins()
        
        if username in users:
            user = users[username]
            return {
                "username": username,
                "email": user.get("email", ""),
                "full_name": user.get("full_name", ""),
                "user_type": "user"
            }
        elif username in admins:
            admin = admins[username]
            return {
                "username": username,
                "email": admin.get("email", ""),
                "full_name": admin.get("full_name", ""),
                "user_type": "admin"
            }
        else:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated admin"""
    user = get_current_user(credentials)
    if user["user_type"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

def initialize_default_users():
    """Initialize default users and admins"""
    # Create default admin
    if not load_admins():
        create_admin(
            username="admin",
            email="admin@mindscope.ai",
            password="admin123",
            full_name="System Administrator"
        )
        print("✅ Created default admin: admin@mindscope.ai / admin123")
    
    # Create default user
    if not load_users():
        create_user(
            username="user1",
            email="user@mindscope.ai",
            password="user123",
            full_name="Test User"
        )
        print("✅ Created default user: user@mindscope.ai / user123")

# Initialize default users on import
initialize_default_users()