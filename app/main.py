from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.routers import tax_relief
from app.middleware.rate_limit import RateLimiter
from app.middleware.timing import add_timing_middleware

app = FastAPI(
    title="Tax Relief API",
    description="API for UK tax relief recommendations",
    version="1.0.0"
)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add rate limiting
app.add_middleware(RateLimiter, requests_per_minute=60)

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
