from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime  # Add this import
from api.auth import verify_token
from services.worksheet_service import WorksheetService

router = APIRouter()
worksheet_service = WorksheetService()

class WorksheetCreate(BaseModel):
    user_id: str
    lead_id: str
    type: str  # e.g., "buyer_order", "deal_pack", etc.
    status: str = "draft"

class WorksheetUpdate(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None

class Worksheet(BaseModel):
    id: str
    user_id: str
    lead_id: str
    type: str
    status: str
    created_at: datetime
    updated_at: datetime

@router.get("/", response_model=List[Worksheet])
async def get_worksheets(lead_id: Optional[str] = None, payload: dict = Depends(verify_token)):
    """Get all worksheets, optionally filtered by lead."""
    try:
        user_id = payload.get("user_id")
        worksheets = worksheet_service.get_all_worksheets(user_id=user_id, lead_id=lead_id)
        return worksheets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Worksheet)
async def create_worksheet(worksheet: WorksheetCreate, payload: dict = Depends(verify_token)):
    """Create a new worksheet."""
    try:
        worksheet_dict = worksheet.dict()
        created_worksheet = worksheet_service.create_worksheet(worksheet_dict)
        return created_worksheet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{worksheet_id}", response_model=Worksheet)
async def get_worksheet(worksheet_id: str, payload: dict = Depends(verify_token)):
    """Get a specific worksheet by ID."""
    try:
        worksheet = worksheet_service.get_worksheet_by_id(worksheet_id)
        if not worksheet:
            raise HTTPException(status_code=404, detail="Worksheet not found")
        return worksheet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{worksheet_id}", response_model=Worksheet)
async def update_worksheet(worksheet_id: str, worksheet: WorksheetUpdate, payload: dict = Depends(verify_token)):
    """Update a worksheet."""
    try:
        update_data = {k: v for k, v in worksheet.dict().items() if v is not None}
        updated_worksheet = worksheet_service.update_worksheet(worksheet_id, update_data)
        if not updated_worksheet:
            raise HTTPException(status_code=404, detail="Worksheet not found")
        return updated_worksheet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{worksheet_id}")
async def delete_worksheet(worksheet_id: str, payload: dict = Depends(verify_token)):
    """Delete a worksheet."""
    try:
        success = worksheet_service.delete_worksheet(worksheet_id)
        if not success:
            raise HTTPException(status_code=404, detail="Worksheet not found")
        return {"message": "Worksheet deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
