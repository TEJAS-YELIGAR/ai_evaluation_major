from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.api.v1.router import router as api_router

setup_logging()

app = FastAPI(
    title="VTU AI Answer Evaluator",
    description="AI-based answer evaluation system for VTU",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routes under /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "VTU AI Evaluator is running!", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}