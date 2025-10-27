"""
Training Center API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.api.auth import get_current_user
from backend.database import get_supabase_client

router = APIRouter(prefix="/api/training", tags=["training"])


class TrainingResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    media_url: Optional[str]
    published: bool
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime


@router.get("/", response_model=List[TrainingResponse])
async def get_training_materials(current_user: dict = Depends(get_current_user)):
    """Get all published training materials."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("training_center") \
            .select("*") \
            .eq("published", True) \
            .order("created_at", desc=True) \
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch training materials: {str(e)}")
