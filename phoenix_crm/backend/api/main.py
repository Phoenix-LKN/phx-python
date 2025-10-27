from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add parent directory to path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Try to import from backend - adjust based on your actual structure
try:
    # Try importing routers from backend.routers
    from backend.routers import auth, leads
except ModuleNotFoundError:
    try:
        # Try importing directly from backend
        from backend import auth, leads
    except ModuleNotFoundError:
        # Create placeholder routers if backend doesn't exist yet
        print("Warning: Backend auth/leads routers not found. Using placeholders.")
        from fastapi import APIRouter
        
        class AuthRouter:
            router = APIRouter(prefix="/api/auth", tags=["auth"])
        
        class LeadsRouter:
            router = APIRouter(prefix="/api/leads", tags=["leads"])
        
        auth = AuthRouter()
        leads = LeadsRouter()

# Import new routers from api.routers
from api.routers import appointments, goals, notifications, worksheets, training

app = FastAPI(title="Phoenix CRM API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(appointments.router)
app.include_router(goals.router)
app.include_router(notifications.router)
app.include_router(worksheets.router)
app.include_router(training.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Phoenix CRM API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "leads": "/api/leads",
            "appointments": "/api/appointments",
            "goals": "/api/goals",
            "notifications": "/api/notifications",
            "worksheets": "/api/worksheets",
            "training": "/api/training"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)