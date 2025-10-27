from typing import List, Optional, Dict, Any
from services.supabase_client import get_supabase_client
from datetime import datetime

class LeadService:
    """Service layer for lead operations."""
    
    def __init__(self):
        self._supabase = None
    
    @property
    def supabase(self):
        """Lazy-load Supabase client."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase
    
    def get_all_leads(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all leads for a user, optionally filtered by status."""
        # IMPORTANT: Filter by assigned_to to ensure users only see their own leads
        query = self.supabase.table("leads").select("*").eq("assigned_to", user_id)
        
        if status:
            query = query.eq("status", status)
        
        response = query.execute()
        return response.data
    
    def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific lead by ID."""
        response = self.supabase.table("leads").select("*").eq("id", lead_id).execute()
        return response.data[0] if response.data else None
    
    def create_lead(self, lead_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new lead."""
        if not lead_data.get("assigned_to"):
            lead_data["assigned_to"] = user_id
        
        lead_data["created_at"] = datetime.utcnow().isoformat()
        lead_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = self.supabase.table("leads").insert(lead_data).execute()
        return response.data[0]
    
    def update_lead(self, lead_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing lead."""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = self.supabase.table("leads").update(update_data).eq("id", lead_id).execute()
        return response.data[0] if response.data else None
    
    def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead."""
        response = self.supabase.table("leads").delete().eq("id", lead_id).execute()
        return bool(response.data)
    
    def get_leads_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get leads filtered by status."""
        response = self.supabase.table("leads").select("*").eq("status", status).execute()
        return response.data
    
    def assign_lead(self, lead_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Assign a lead to a user."""
        return self.update_lead(lead_id, {"assigned_to": user_id})
