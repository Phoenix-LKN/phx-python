from dotenv import load_dotenv

# Load environment variables FIRST, before any other imports
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, leads, users, worksheets
import uvicorn

app = FastAPI(
    title="Phoenix CRM API",
    description="The backend API for the Phoenix CRM application.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Verify configuration on startup."""
    import os
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    
    print("=" * 50)
    print("STARTUP CONFIGURATION CHECK")
    print("=" * 50)
    print(f"SUPABASE_URL: {supabase_url[:30]}..." if supabase_url else "SUPABASE_URL: NOT SET")
    print(f"SUPABASE_KEY: {supabase_key[:20]}..." if supabase_key else "SUPABASE_KEY: NOT SET")
    print(f"JWT_SECRET_KEY: {'SET' if jwt_secret else 'NOT SET'}")
    print("=" * 50)
    
    if not supabase_url or not supabase_key:
        print("⚠️  WARNING: Supabase credentials not properly configured!")
        print("⚠️  Make sure .env file is in the backend directory")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(worksheets.router, prefix="/api/worksheets", tags=["Worksheets"])

@app.get("/", tags=["Root"])
async def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"message": "Welcome to the Phoenix CRM API!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
