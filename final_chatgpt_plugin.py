"""
Final Working ChatGPT Plugin

This addresses the serialization issues by properly formatting data
before returning it to FastAPI.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json

app = FastAPI(
    title="Quilt Database Search Plugin",
    description="Search through indexed content for ChatGPT",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class SearchResult(BaseModel):
    rank: int
    content: str
    score: float
    metadata: Dict[str, Any]
    search_type: str

class SearchResponse(BaseModel):
    query: str
    search_type: str
    total_results: int
    results: List[SearchResult]

# Global search engine
search_engine = None

def get_search_engine():
    global search_engine
    if search_engine is None:
        from postgres_hybrid_search import PostgresHybridVectorSearch
        search_engine = PostgresHybridVectorSearch()
    return search_engine

def clean_result(result: Dict) -> Dict:
    """Clean a search result to ensure it's JSON serializable"""
    return {
        "content": str(result.get("content", ""))[:500],  # Limit content length
        "score": float(result.get("score", 0.0)),
        "metadata": dict(result.get("metadata", {})),
        "search_type": str(result.get("search_type", "unknown")),
        "created_at": str(result.get("created_at", "")) if result.get("created_at") else None
    }

@app.get("/.well-known/ai-plugin.json")
async def get_plugin_manifest():
    """Plugin manifest for ChatGPT"""
    return {
        "schema_version": "v1",
        "name_for_human": "Quilt Database Search",
        "name_for_model": "quilt_search",
        "description_for_human": "Search through your indexed content database to find relevant information",
        "description_for_model": "Search through indexed content using semantic search, keyword search, or hybrid search. Returns relevant documents with content and metadata that can be used to answer questions with accurate, sourced information.",
        "auth": {"type": "none"},
        "api": {
            "type": "openapi",
            "url": "http://localhost:8000/openapi.json"
        },
        "logo_url": "http://localhost:8000/logo.png",
        "contact_email": "support@quilt.com"
    }

@app.get("/search", response_model=SearchResponse)
async def search_database(
    query: str = Query(..., description="The search query to find relevant content"),
    max_results: int = Query(5, description="Maximum number of results to return", ge=1, le=20),
    search_type: str = Query("keyword", description="Type of search: 'hybrid', 'vector', or 'keyword'")
):
    """Search the database for relevant content"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get search engine
        engine = get_search_engine()
        
        # Perform search based on type
        if search_type == "vector":
            raw_results = engine.vector_search(query, k=max_results)
        elif search_type == "hybrid":
            raw_results = engine.search_similar(query, k=max_results)
        else:  # keyword (default)
            raw_results = engine.keyword_search(query, k=max_results)
        
        # Clean and format results
        formatted_results = []
        for i, result in enumerate(raw_results, 1):
            cleaned = clean_result(result)
            formatted_results.append(SearchResult(
                rank=i,
                content=cleaned["content"],
                score=cleaned["score"],
                metadata=cleaned["metadata"],
                search_type=cleaned["search_type"]
            ))
        
        return SearchResponse(
            query=query,
            search_type=search_type,
            total_results=len(formatted_results),
            results=formatted_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/stats")
async def get_database_stats():
    """Get statistics about the database content"""
    try:
        engine = get_search_engine()
        stats = engine.get_stats()
        
        return {
            "database_info": {
                "total_documents": int(stats.get("total_documents", 0)),
                "documents_with_embeddings": int(stats.get("documents_with_embeddings", 0)),
                "unique_words": int(stats.get("unique_words", 0)),
                "database_type": str(stats.get("database", "PostgreSQL")),
                "embedding_model": str(stats.get("embedding_model", "Unknown")),
                "search_capabilities": ["keyword", "hybrid", "vector"]
            },
            "usage_info": "This database contains indexed content that can be searched semantically or by keywords to provide accurate, sourced information."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        engine = get_search_engine()
        stats = engine.get_stats()
        
        return {
            "status": "healthy",
            "database_connected": True,
            "total_documents": int(stats.get("total_documents", 0)),
            "search_ready": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e),
            "search_ready": False
        }

@app.get("/")
async def root():
    """Root endpoint with plugin information"""
    return {
        "name": "Quilt Database Search Plugin",
        "description": "ChatGPT plugin for searching indexed content",
        "version": "1.0.0",
        "endpoints": {
            "search": "/search - Search the database",
            "stats": "/stats - Get database statistics", 
            "health": "/health - Health check",
            "manifest": "/.well-known/ai-plugin.json - Plugin manifest"
        },
        "usage": "Use this plugin to search through indexed content and provide accurate, sourced answers."
    }

if __name__ == "__main__":
    print("🚀 Starting Quilt ChatGPT Plugin...")
    uvicorn.run(
        "final_chatgpt_plugin:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
