from typing import List, Optional, Dict, Any
from services.supabase_client import get_supabase_client
from datetime import datetime

class WorksheetService:
    """Service layer for worksheet operations."""
    
    def __init__(self):
        self._supabase = None
    
    @property
    def supabase(self):
        """Lazy-load Supabase client."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase
    
    def get_all_worksheets(self, user_id: Optional[str] = None, lead_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get worksheets, optionally filtered by user or lead."""
        query = self.supabase.table("worksheets").select("*")
        
        if user_id:
            query = query.eq("user_id", user_id)
        if lead_id:
            query = query.eq("lead_id", lead_id)
        
        response = query.execute()
        return response.data
    
    def get_worksheet_by_id(self, worksheet_id: str) -> Optional[Dict[str, Any]]:
        """Get a worksheet by ID."""
        response = self.supabase.table("worksheets").select("*").eq("id", worksheet_id).execute()
        return response.data[0] if response.data else None
    
    def create_worksheet(self, worksheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new worksheet."""
        worksheet_data["created_at"] = datetime.utcnow().isoformat()
        worksheet_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = self.supabase.table("worksheets").insert(worksheet_data).execute()
        return response.data[0]
    
    def update_worksheet(self, worksheet_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a worksheet."""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = self.supabase.table("worksheets").update(update_data).eq("id", worksheet_id).execute()
        return response.data[0] if response.data else None
    
    def delete_worksheet(self, worksheet_id: str) -> bool:
        """Delete a worksheet."""
        response = self.supabase.table("worksheets").delete().eq("id", worksheet_id).execute()
        return bool(response.data)
