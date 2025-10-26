from supabase import create_client, Client
import os
from functools import lru_cache

@lru_cache()
def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    
    supabase = create_client(url, key)
    return supabase
