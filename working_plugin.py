"""
Working ChatGPT Plugin with proper error handling
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import traceback
import uvicorn
import os

app = FastAPI(
    title="Quilt Database Search Plugin",
    description="Search through indexed content",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global search engine instance
search_engine = None

def get_search_engine():
    global search_engine
    if search_engine is None:
        try:
            from postgres_hybrid_search import PostgresHybridVectorSearch
            search_engine = PostgresHybridVectorSearch()
            print("✅ Search engine initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize search engine: {e}")
            traceback.print_exc()
            raise e
    return search_engine

@app.get("/.well-known/ai-plugin.json")
async def get_plugin_manifest():
    """Plugin manifest for ChatGPT"""
    return {
        "schema_version": "v1",
        "name_for_human": "Quilt Database Search",
        "name_for_model": "quilt_search",
        "description_for_human": "Search through your indexed content database",
        "description_for_model": "Search through indexed content using keyword search or hybrid search. Returns relevant documents that can be used to answer questions.",
        "auth": {"type": "none"},
        "api": {
            "type": "openapi",
            "url": "http://localhost:8000/openapi.json"
        },
        "logo_url": "http://localhost:8000/logo.png",
        "contact_email": "support@quilt.com"
    }

@app.get("/search")
async def search_database(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(5, description="Max results", ge=1, le=20),
    search_type: str = Query("keyword", description="Search type: keyword, hybrid, or vector")
):
    """Search the database for relevant content"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        print(f"🔍 Search request: '{query}' ({search_type})")
        
        # Get search engine
        engine = get_search_engine()
        
        # Perform search
        if search_type == "vector":
            results = engine.vector_search(query, k=max_results)
        elif search_type == "hybrid":
            results = engine.search_similar(query, k=max_results)
        else:  # keyword (default)
            results = engine.keyword_search(query, k=max_results)
        
        print(f"✅ Found {len(results)} results")
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "rank": i,
                "content": result["content"][:500],  # Limit content
                "score": round(result["score"], 3),
                "metadata": result.get("metadata", {}),
                "search_type": result.get("search_type", search_type)
            })
        
        return {
            "query": query,
            "search_type": search_type,
            "total_results": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        error_msg = f"Search error: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        engine = get_search_engine()
        stats = engine.get_stats()
        
        return {
            "database_info": {
                "total_documents": stats.get("total_documents", 0),
                "documents_with_embeddings": stats.get("documents_with_embeddings", 0),
                "database_type": stats.get("database", "PostgreSQL"),
                "search_capabilities": ["keyword", "hybrid", "vector"]
            }
        }
    except Exception as e:
        error_msg = f"Stats error: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/health")
async def health_check():
    """Health check"""
    try:
        engine = get_search_engine()
        stats = engine.get_stats()
        
        return {
            "status": "healthy",
            "database_connected": True,
            "total_documents": stats.get("total_documents", 0)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Quilt Database Search Plugin",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/search", "/stats", "/health", "/.well-known/ai-plugin.json"]
    }

if __name__ == "__main__":
    print("🚀 Starting Quilt ChatGPT Plugin...")
    uvicorn.run(
        "working_plugin:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
