"""
Worksheets API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.api.auth import get_current_user
from backend.database import get_supabase_client

router = APIRouter(prefix="/api/worksheets", tags=["worksheets"])


class WorksheetResponse(BaseModel):
    id: str
    user_id: str
    title: str
    type: Optional[str]
    data: Optional[Dict[str, Any]]
    status: str
    last_modified: datetime
    created_at: datetime


@router.get("/", response_model=List[WorksheetResponse])
async def get_worksheets(current_user: dict = Depends(get_current_user)):
    """Get all worksheets for the current user."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("worksheets") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .order("last_modified", desc=True) \
            .execute()
        
        # Handle case where table doesn't exist or has no data
        if not response.data:
            return []
        
        return response.data
    except Exception as e:
        print(f"Error fetching worksheets: {e}")
        # Return empty array instead of failing
        return []
