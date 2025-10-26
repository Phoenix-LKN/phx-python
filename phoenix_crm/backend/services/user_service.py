from typing import List, Optional, Dict, Any
from services.supabase_client import get_supabase_client
from datetime import datetime

class UserService:
    """Service layer for user operations."""
    
    def __init__(self):
        self._supabase = None
    
    @property
    def supabase(self):
        """Lazy-load Supabase client."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        response = self.supabase.table("users").select("*").execute()
        return response.data
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID."""
        response = self.supabase.table("users").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email."""
        response = self.supabase.table("users").select("*").eq("email", email).execute()
        return response.data[0] if response.data else None
    
    def create_user_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a user profile."""
        user_data["created_at"] = datetime.utcnow().isoformat()
        user_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = self.supabase.table("users").insert(user_data).execute()
        return response.data[0]
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a user profile."""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
        return response.data[0] if response.data else None
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """Get all active users."""
        response = self.supabase.table("users").select("*").eq("status", "active").execute()
        return response.data
