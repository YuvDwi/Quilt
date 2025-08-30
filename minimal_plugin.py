"""
Minimal ChatGPT Plugin for testing
"""

from fastapi import FastAPI
import uvicorn
import sys
import traceback

app = FastAPI()

@app.get("/.well-known/ai-plugin.json")
async def manifest():
    return {
        "schema_version": "v1",
        "name_for_human": "Quilt Search",
        "name_for_model": "quilt",
        "description_for_human": "Search database",
        "description_for_model": "Search through content",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": "http://localhost:8000/openapi.json"}
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/search")
async def search(query: str = "test"):
    try:
        print(f"🔍 Searching for: {query}")
        
        # Test direct function call first
        from debug_search import test_search_directly
        if test_search_directly():
            print("✅ Direct search works")
        else:
            print("❌ Direct search failed")
            return {"error": "Direct search failed"}
        
        # Now try the actual search
        from postgres_hybrid_search import PostgresHybridVectorSearch
        print("✅ Import successful")
        
        engine = PostgresHybridVectorSearch()
        print("✅ Engine created")
        
        results = engine.keyword_search(query, k=3)
        print(f"✅ Search completed: {len(results)} results")
        
        return {
            "query": query,
            "results": results,
            "status": "success"
        }
        
    except Exception as e:
        error_info = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(f"❌ Error: {error_info}")
        return error_info

if __name__ == "__main__":
    print("🚀 Starting minimal plugin...")
    uvicorn.run("minimal_plugin:app", host="0.0.0.0", port=8002, log_level="debug")
