from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tax_relief

app = FastAPI(
    title="Tax Relief API",
    description="API for UK tax relief recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tax_relief.router, prefix="/api")
