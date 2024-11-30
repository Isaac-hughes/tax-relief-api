from fastapi import Request
import time
import logging

logger = logging.getLogger(__name__)

async def add_timing_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Request to {request.url.path} took {process_time:.2f} seconds")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response 