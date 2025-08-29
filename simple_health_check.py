#!/usr/bin/env python3

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Quilt Simple API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Quilt API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "app": "Quilt Simple API",
        "port": os.getenv("PORT", "8005"),
        "env_vars": {
            "GITHUB_CLIENT_ID": "SET" if os.getenv("GITHUB_CLIENT_ID") else "NOT SET",
            "GITHUB_CLIENT_SECRET": "SET" if os.getenv("GITHUB_CLIENT_SECRET") else "NOT SET",
            "COHERE_API_KEY": "SET" if os.getenv("COHERE_API_KEY") else "NOT SET"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
