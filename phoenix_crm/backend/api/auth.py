from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from services.supabase_client import get_supabase_client
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None
    role: Optional[str] = "user"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt

def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    supabase = get_supabase_client()
    
    try:
        print(f"Attempting login for: {request.email}")
        
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        print(f"Auth successful for user: {response.user.id}")
        
        # Try to get user profile, but don't fail if it doesn't exist
        try:
            user_data = supabase.table("users").select("*").eq("id", response.user.id).execute()
            user_info = user_data.data[0] if user_data.data else None
        except Exception as profile_error:
            print(f"Could not fetch user profile: {profile_error}")
            user_info = None
        
        # If no profile exists, create a basic one or use auth data
        if not user_info:
            print(f"No user profile found, using auth data")
            user_info = {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.email.split('@')[0],  # Use email prefix as name
                "role": "user"
            }
        
        # Create JWT token
        token = create_access_token({
            "user_id": response.user.id,
            "email": response.user.email
        })
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user_info
        )
        
    except Exception as e:
        print(f"Login error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")

@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    supabase = get_supabase_client()
    
    try:
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        # Create user profile
        user_profile = supabase.table("users").insert({
            "id": auth_response.user.id,
            "email": request.email,
            "full_name": request.full_name,
            "phone_number": request.phone_number,
            "role": request.role
        }).execute()
        
        token = create_access_token({
            "user_id": auth_response.user.id,
            "email": request.email
        })
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user_profile.data[0]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def logout(payload: dict = Depends(verify_token)):
    supabase = get_supabase_client()
    supabase.auth.sign_out()
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    supabase = get_supabase_client()
    user_id = payload.get("user_id")
    
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return response.data[0]
