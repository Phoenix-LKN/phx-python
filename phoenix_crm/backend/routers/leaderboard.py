"""
Leaderboard API Router - Track top performing sales people
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.api.auth import get_current_user
from backend.database import get_supabase_client

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


class LeaderboardEntry(BaseModel):
    user_id: str
    full_name: Optional[str] = "Unknown User"  # Allow None and provide default
    email: str
    total_sales: int
    total_revenue: float
    total_commission: float
    avg_deal_size: float
    monthly_sales: int
    monthly_revenue: float
    weekly_sales: int
    weekly_revenue: float
    last_sale_date: Optional[str]
    rank: Optional[int] = None


@router.get("/", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    period: str = Query(default="all", regex="^(all|monthly|weekly)$"),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """
    Get sales leaderboard.
    
    - **period**: Filter by time period (all, monthly, weekly)
    - **limit**: Number of top performers to return (1-50)
    """
    supabase = get_supabase_client()
    
    try:
        # Refresh the materialized view (in production, do this on a schedule)
        supabase.rpc('refresh_leaderboard').execute()
        
        # Fetch leaderboard data
        query = supabase.table("sales_leaderboard").select("*")
        
        # Order by appropriate metric based on period
        if period == "monthly":
            query = query.order("monthly_revenue", desc=True)
        elif period == "weekly":
            query = query.order("weekly_revenue", desc=True)
        else:
            query = query.order("total_revenue", desc=True)
        
        query = query.limit(limit)
        
        response = query.execute()
        
        # Add rank to each entry
        leaderboard = response.data
        for idx, entry in enumerate(leaderboard, start=1):
            entry['rank'] = idx
        
        return leaderboard
        
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch leaderboard: {str(e)}")


@router.get("/my-stats")
async def get_my_stats(current_user: dict = Depends(get_current_user)):
    """Get current user's sales statistics."""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("sales_leaderboard") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not response.data:
            # Return zero stats if user has no sales yet
            return {
                "user_id": current_user["id"],
                "total_sales": 0,
                "total_revenue": 0,
                "monthly_sales": 0,
                "monthly_revenue": 0,
                "rank": None
            }
        
        # Get user's rank
        all_users = supabase.table("sales_leaderboard") \
            .select("user_id, total_revenue") \
            .order("total_revenue", desc=True) \
            .execute()
        
        rank = next((idx + 1 for idx, user in enumerate(all_users.data) 
                    if user["user_id"] == current_user["id"]), None)
        
        stats = response.data
        stats['rank'] = rank
        
        return stats
        
    except Exception as e:
        print(f"Error fetching user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
