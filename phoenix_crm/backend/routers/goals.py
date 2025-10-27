"""
Goals API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from backend.api.auth import get_current_user
from backend.database import get_supabase_client

router = APIRouter(prefix="/api/goals", tags=["goals"])


class GoalResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    target_value: Optional[float]
    current_value: Optional[float]
    progress: Optional[float]
    deadline: Optional[date]
    status: str
    created_at: datetime
    updated_at: datetime


@router.get("/", response_model=List[GoalResponse])
async def get_goals(current_user: dict = Depends(get_current_user)):
    """Get all goals for the current user."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("goals") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .order("created_at", desc=True) \
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch goals: {str(e)}")
