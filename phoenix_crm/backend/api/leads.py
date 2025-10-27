from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from backend.api.auth import get_current_user
from services.lead_service import LeadService

router = APIRouter(prefix="/api/leads", tags=["leads"])  # Add prefix here
lead_service = LeadService()

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None
    status: str = "new"
    priority: Optional[str] = "medium"
    value: Optional[float] = None
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    assigned_to: Optional[str] = None

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    value: Optional[float] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None

class Lead(LeadBase):
    id: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime

@router.get("/", response_model=List[Lead])
async def get_leads(current_user: dict = Depends(get_current_user)):
    """Get all leads for the current user."""
    try:
        user_id = current_user.get("id")
        print(f"Fetching leads for user_id: {user_id}")  # Debug log
        
        leads = lead_service.get_all_leads(user_id)
        
        print(f"Found {len(leads)} leads")  # Debug log
        
        return leads
    except Exception as e:
        print(f"Error fetching leads: {type(e).__name__}: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Lead)
async def create_lead(lead: LeadCreate, current_user: dict = Depends(get_current_user)):
    """Create a new lead."""
    try:
        user_id = current_user.get("id")
        lead_dict = lead.dict()
        created_lead = lead_service.create_lead(lead_dict, user_id)
        return created_lead
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific lead by ID."""
    try:
        lead = lead_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{lead_id}", response_model=Lead)
async def update_lead(lead_id: str, lead: LeadUpdate, current_user: dict = Depends(get_current_user)):
    """Update a lead."""
    try:
        update_data = {k: v for k, v in lead.dict().items() if v is not None}
        updated_lead = lead_service.update_lead(lead_id, update_data)
        if not updated_lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return updated_lead
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a lead."""
    try:
        success = lead_service.delete_lead(lead_id)
        if not success:
            raise HTTPException(status_code=404, detail="Lead not found")
        return {"message": "Lead deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
