"""
Notifications API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from pydantic import BaseModel
from backend.api.auth import get_current_user
from backend.database import get_supabase_client

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    read: bool
    created_at: datetime


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    """Get all notifications for the current user."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("notifications") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .order("created_at", desc=True) \
            .limit(50) \
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


@router.patch("/{notification_id}/read")
async def mark_as_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a notification as read."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("notifications") \
            .update({"read": True}) \
            .eq("id", notification_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update notification: {str(e)}")
