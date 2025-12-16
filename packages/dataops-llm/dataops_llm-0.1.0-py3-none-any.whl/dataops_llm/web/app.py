"""FastAPI application for DataOps LLM Engine."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dataops_llm import __version__
from dataops_llm.web.routes import router

# Create FastAPI application
app = FastAPI(
    title="DataOps LLM Engine API",
    description="LLM-powered data operations for Excel/CSV files via REST API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["data-operations"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "DataOps LLM Engine API",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "dataops_llm.web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
