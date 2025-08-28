#!/usr/bin/env python3

import os
from fastapi import FastAPI
from datetime import datetime

# Minimal health check app with ZERO dependencies
health_app = FastAPI(title="Health Check")

@health_app.get("/health")
async def health_check():
    """Ultra-lightweight health check - no imports, no database, no nothing"""
    return {
        "status": "healthy",
        "service": "quilt-backend", 
        "port": os.getenv("PORT", "8005"),
        "timestamp": str(datetime.now()),
        "message": "Service is running"
    }

@health_app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Health check service running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8005))
    uvicorn.run(health_app, host="0.0.0.0", port=port)
