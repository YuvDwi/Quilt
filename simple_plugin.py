"""
Simple ChatGPT Plugin for debugging
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Simple Quilt Plugin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/.well-known/ai-plugin.json")
async def get_manifest():
    return {
        "schema_version": "v1",
        "name_for_human": "Simple Quilt Search",
        "name_for_model": "simple_quilt",
        "description_for_human": "Simple search plugin",
        "description_for_model": "Search through content",
        "auth": {"type": "none"},
        "api": {
            "type": "openapi",
            "url": "http://localhost:8001/openapi.json"
        }
    }

@app.get("/search")
async def search(query: str, max_results: int = 5):
    try:
        # Import here to avoid startup issues
        from postgres_hybrid_search import PostgresHybridVectorSearch
        
        search_engine = PostgresHybridVectorSearch()
        results = search_engine.keyword_search(query, k=max_results)
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results[:max_results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Simple plugin is running"}

if __name__ == "__main__":
    uvicorn.run("simple_plugin:app", host="0.0.0.0", port=8001, reload=True)
