#!/usr/bin/env python3

import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Quilt Simple API")

@app.get("/")
async def root():
    """Simple root endpoint"""
    return {
        "message": "Quilt Simple API is running",
        "port": os.getenv("PORT", "8005"),
        "status": "healthy"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "service": "quilt-simple"}

@app.get("/test")
async def test():
    """Test endpoint"""
    return {"test": "success", "message": "API is working"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8005))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
