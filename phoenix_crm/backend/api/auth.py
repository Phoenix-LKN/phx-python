"""
Authentication API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from backend.database import get_supabase_client

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Login endpoint for Supabase authentication."""
    supabase = get_supabase_client()
    
    try:
        print(f"Attempting login for: {credentials.email}")
        
        # Authenticate with Supabase
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        print(f"Supabase response: {response}")
        
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "access_token": response.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.user_metadata.get("full_name", ""),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


@router.post("/signup")
async def register(credentials: LoginRequest):
    """Register a new user."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not response.user:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        return {"message": "User registered successfully", "user_id": response.user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user from the JWT token."""
    supabase = get_supabase_client()
    token = credentials.credentials
    
    try:
        # Verify the token with Supabase
        user = supabase.auth.get_user(token)
        
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        return {"id": user.user.id, "email": user.user.email}
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout the current user."""
    supabase = get_supabase_client()
    
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")
