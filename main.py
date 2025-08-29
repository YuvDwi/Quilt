import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Quilt API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Railway will auto-detect this
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
