"""
ChatGPT Plugin API for Quilt Database Search

This creates a ChatGPT-compatible plugin that allows ChatGPT to search
your database and include relevant information in its responses.
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from postgres_hybrid_search import PostgresHybridVectorSearch
import uvicorn

# Initialize the search engine (lazy initialization)
search_engine = None

def get_search_engine():
    global search_engine
    if search_engine is None:
        search_engine = PostgresHybridVectorSearch()
    return search_engine

# Create FastAPI app
app = FastAPI(
    title="Quilt Database Search Plugin",
    description="A ChatGPT plugin that provides semantic search capabilities over your indexed content",
    version="1.0.0"
)

# Add CORS middleware for ChatGPT compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    search_type: Optional[str] = "hybrid"

class SearchResult(BaseModel):
    content: str
    score: float
    metadata: Dict[str, Any]
    search_type: str

@app.get("/.well-known/ai-plugin.json")
async def get_plugin_manifest():
    """Plugin manifest for ChatGPT"""
    return {
        "schema_version": "v1",
        "name_for_human": "Quilt Database Search",
        "name_for_model": "quilt_search",
        "description_for_human": "Search through your indexed content database to find relevant information",
        "description_for_model": "Search through indexed content using semantic search, keyword search, or hybrid search. Returns relevant documents with content and metadata that can be used to answer questions with accurate, sourced information.",
        "auth": {
            "type": "none"
        },
        "api": {
            "type": "openapi",
            "url": f"{os.getenv('PLUGIN_URL', 'http://localhost:8000')}/openapi.json"
        },
        "logo_url": f"{os.getenv('PLUGIN_URL', 'http://localhost:8000')}/logo.png",
        "contact_email": "support@quilt.com",
        "legal_info_url": f"{os.getenv('PLUGIN_URL', 'http://localhost:8000')}/legal"
    }

@app.get("/search")
async def search_database(
    query: str = Query(..., description="The search query to find relevant content"),
    max_results: int = Query(5, description="Maximum number of results to return", ge=1, le=20),
    search_type: str = Query("hybrid", description="Type of search: 'hybrid', 'vector', or 'keyword'")
):
    """
    Search the database for relevant content.
    
    This endpoint allows ChatGPT to search through your indexed content
    and retrieve relevant information to help answer user questions.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get search engine instance
        engine = get_search_engine()
        
        # Perform the search based on type
        if search_type == "vector":
            results = engine.vector_search(query, k=max_results)
        elif search_type == "keyword":
            results = engine.keyword_search(query, k=max_results)
        else:  # hybrid (default)
            results = engine.search_similar(query, k=max_results)
        
        # Format results for ChatGPT
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "rank": i,
                "content": result["content"][:1000],  # Limit content length
                "score": round(result["score"], 3),
                "metadata": result.get("metadata", {}),
                "search_type": result.get("search_type", search_type),
                "created_at": result.get("created_at")
            })
        
        return {
            "query": query,
            "search_type": search_type,
            "total_results": len(formatted_results),
            "results": formatted_results,
            "suggestion": f"Found {len(formatted_results)} relevant documents for '{query}'. Use this information to provide an accurate, well-sourced answer."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/search")
async def search_database_post(request: SearchRequest):
    """
    Alternative POST endpoint for searching the database.
    """
    return await search_database(
        query=request.query,
        max_results=request.max_results,
        search_type=request.search_type
    )

@app.get("/stats")
async def get_database_stats():
    """
    Get statistics about the database content.
    
    Useful for ChatGPT to understand what kind of information is available.
    """
    try:
        engine = get_search_engine()
        stats = engine.get_stats()
        return {
            "database_info": {
                "total_documents": stats.get("total_documents", 0),
                "documents_with_embeddings": stats.get("documents_with_embeddings", 0),
                "unique_words": stats.get("unique_words", 0),
                "database_type": stats.get("database", "PostgreSQL"),
                "embedding_model": stats.get("embedding_model", "Unknown"),
                "search_capabilities": ["hybrid", "vector", "keyword", "tfidf"]
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
            "total_documents": stats.get("total_documents", 0),
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

# Add custom OpenAPI specification for better ChatGPT integration
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = {
        "openapi": "3.0.1",
        "info": {
            "title": "Quilt Database Search Plugin",
            "description": "Search through indexed content to find relevant information for answering questions",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": os.getenv('PLUGIN_URL', 'http://localhost:8000')
            }
        ],
        "paths": {
            "/search": {
                "get": {
                    "operationId": "searchDatabase",
                    "summary": "Search the content database",
                    "description": "Search through indexed content using semantic search, keyword search, or hybrid search to find relevant information",
                    "parameters": [
                        {
                            "name": "query",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "The search query to find relevant content"
                        },
                        {
                            "name": "max_results",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                            "description": "Maximum number of results to return"
                        },
                        {
                            "name": "search_type",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "enum": ["hybrid", "vector", "keyword"], "default": "hybrid"},
                            "description": "Type of search to perform"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Search results",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {"type": "string"},
                                            "search_type": {"type": "string"},
                                            "total_results": {"type": "integer"},
                                            "results": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "rank": {"type": "integer"},
                                                        "content": {"type": "string"},
                                                        "score": {"type": "number"},
                                                        "metadata": {"type": "object"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/stats": {
                "get": {
                    "operationId": "getDatabaseStats",
                    "summary": "Get database statistics",
                    "description": "Get information about the database content and capabilities",
                    "responses": {
                        "200": {
                            "description": "Database statistics",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "database_info": {"type": "object"},
                                            "usage_info": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(
        "chatgpt_plugin_api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
