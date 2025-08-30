"""
Simple ChatGPT Plugin that works with basic search
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

app = FastAPI(
    title="Quilt Database Search Plugin",
    description="Search through indexed content for ChatGPT",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchResult(BaseModel):
    rank: int
    content: str
    score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]

def simple_search(query: str, max_results: int = 5) -> List[Dict]:
    """Simple search using direct database query"""
    try:
        from database_config import get_db, Document
        
        db = next(get_db())
        try:
            # Simple text search in content
            documents = db.query(Document).filter(
                Document.content.ilike(f"%{query}%")
            ).limit(max_results).all()
            
            results = []
            for i, doc in enumerate(documents, 1):
                # Calculate simple relevance score
                content_lower = doc.content.lower()
                query_lower = query.lower()
                score = content_lower.count(query_lower) / len(content_lower.split())
                
                results.append({
                    "rank": i,
                    "content": doc.content[:400],  # Limit content
                    "score": round(score, 3),
                    "metadata": doc.doc_metadata or {},
                    "id": doc.id,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None
                })
            
            return results
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Search error: {e}")
        return []

@app.get("/.well-known/ai-plugin.json")
async def get_plugin_manifest():
    return {
        "schema_version": "v1",
        "name_for_human": "Quilt Database Search",
        "name_for_model": "quilt_search",
        "description_for_human": "Search through your indexed content database",
        "description_for_model": "Search through indexed content to find relevant information that can help answer questions with accurate, sourced data.",
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
    query: str = Query(..., description="Search query"),
    max_results: int = Query(5, description="Max results", ge=1, le=20)
):
    """Search the database"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Perform simple search
        raw_results = simple_search(query, max_results)
        
        # Format results
        results = []
        for result in raw_results:
            results.append(SearchResult(
                rank=result["rank"],
                content=result["content"],
                score=result["score"],
                metadata=result["metadata"]
            ))
        
        return SearchResponse(
            query=query,
            total_results=len(results),
            results=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get database stats"""
    try:
        from database_config import get_db, Document
        
        db = next(get_db())
        try:
            total_docs = db.query(Document).count()
            return {
                "database_info": {
                    "total_documents": total_docs,
                    "database_type": "PostgreSQL",
                    "search_type": "text_matching"
                }
            }
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check"""
    try:
        from database_config import get_db, Document
        
        db = next(get_db())
        try:
            count = db.query(Document).count()
            return {
                "status": "healthy",
                "total_documents": count
            }
        finally:
            db.close()
            
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/")
async def root():
    return {
        "name": "Quilt Database Search Plugin",
        "version": "1.0.0",
        "status": "running",
        "description": "Simple search plugin for ChatGPT"
    }

if __name__ == "__main__":
    print("🚀 Starting Simple Quilt Plugin...")
    uvicorn.run("simple_search_plugin:app", host="0.0.0.0", port=8001, reload=False)
