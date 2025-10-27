"""
Appointments API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# Import from your existing backend.api structure
from backend.api.auth import get_current_user
from backend.database import get_supabase_client

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


class AppointmentResponse(BaseModel):
    id: str
    user_id: str
    client_name: str
    appointment_title: Optional[str]
    appointment_time: datetime
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(current_user: dict = Depends(get_current_user)):
    """Get all appointments for the current user."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("appointments") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .order("appointment_time", desc=False) \
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch appointments: {str(e)}")


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific appointment."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("appointments") \
            .select("*") \
            .eq("id", appointment_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch appointment: {str(e)}")
