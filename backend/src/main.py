from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="CheckList backend API with RAG capabilities"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CheckList API",
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Import and include routers
from src.routes import files, comparison, rag, checklist
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(comparison.router, prefix="/api/comparison", tags=["comparison"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(checklist.router, prefix="/api/checklist", tags=["checklist"])