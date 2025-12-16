"""
MindScope AI - Authentication API Routes
Handles user and admin authentication
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from utils.auth import (
    authenticate_user, authenticate_admin, create_user, create_admin,
    get_current_user, get_current_admin, create_access_token
)

router = APIRouter()
security = HTTPBearer()

# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str
    user_type: str  # "user" or "admin"

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = ""
    user_type: str  # "user" or "admin"

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class RegisterResponse(BaseModel):
    message: str
    user: dict

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user or admin"""
    try:
        if request.user_type == "admin":
            user = authenticate_admin(request.username, request.password)
        else:
            user = authenticate_user(request.username, request.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user["username"], "user_type": user["user_type"]},
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """Register new user or admin"""
    try:
        if request.user_type == "admin":
            success = create_admin(
                username=request.username,
                email=request.email,
                password=request.password,
                full_name=request.full_name
            )
        else:
            success = create_user(
                username=request.username,
                email=request.email,
                password=request.password,
                full_name=request.full_name
            )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        user_data = {
            "username": request.username,
            "email": request.email,
            "full_name": request.full_name,
            "user_type": request.user_type
        }
        
        return RegisterResponse(
            message="Registration successful",
            user=user_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify JWT token"""
    return {"valid": True, "user": current_user}

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Logout successful"}

@router.get("/test-credentials")
async def get_test_credentials():
    """Get test credentials for demo"""
    return {
        "admin": {
            "username": "admin",
            "password": "admin123",
            "user_type": "admin"
        },
        "user": {
            "username": "user1",
            "password": "user123",
            "user_type": "user"
        }
    }
