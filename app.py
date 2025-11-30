"""
FastAPI Application for Budget Tracker Agent API

Run with:
    uvicorn app:app --reload --host 0.0.0.0 --port 8000

Or:
    python app.py
"""

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Budget Tracker Agent API",
    description="REST API for budget tracking and analysis with natural language support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Budget Tracker Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    # Use reload=False when running directly, or use: uvicorn app:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

