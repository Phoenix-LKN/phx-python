from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from services.supabase_client import get_supabase_client
from datetime import datetime
from api.auth import verify_token
from services.user_service import UserService

router = APIRouter()
user_service = UserService()

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    role: str = "user"
    department: Optional[str] = None
    status: str = "active"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

@router.get("/", response_model=List[User])
async def get_users(payload: dict = Depends(verify_token)):
    """Get all users."""
    try:
        users = user_service.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, payload: dict = Depends(verify_token)):
    """Get a specific user by ID."""
    try:
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserUpdate, payload: dict = Depends(verify_token)):
    """Update a user."""
    try:
        # Only allow users to update themselves or admins to update anyone
        if payload.get("user_id") != user_id:
            # TODO: Check if user is admin
            pass
        
        update_data = {k: v for k, v in user.dict().items() if v is not None}
        updated_user = user_service.update_user(user_id, update_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
