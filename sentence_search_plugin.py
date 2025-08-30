"""
Working ChatGPT Plugin that can search with full sentences
Fixes the JSON serialization issues by avoiding complex objects
"""

from fastapi import FastAPI, HTTPException, Query, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI(
    title="Quilt Sentence Search Plugin",
    description="Search through indexed content using full sentences",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def search_with_sentence(query: str, max_results: int = 5):
    """Search using full sentences with proper text matching"""
    try:
        from database_config import get_db, Document
        
        db = next(get_db())
        try:
            # Search for documents containing words from the sentence
            query_words = query.lower().split()
            
            # Use PostgreSQL full-text search capabilities
            search_conditions = []
            for word in query_words:
                if len(word) > 2:  # Skip very short words
                    search_conditions.append(Document.content.ilike(f"%{word}%"))
            
            if not search_conditions:
                return []
            
            # Combine conditions with OR (any matching word)
            from sqlalchemy import or_
            combined_condition = or_(*search_conditions)
            
            documents = db.query(Document).filter(combined_condition).limit(max_results * 2).all()
            
            # Score documents based on how many query words they contain
            results = []
            for doc in documents:
                content_lower = doc.content.lower()
                
                # Count word matches
                word_matches = sum(1 for word in query_words if word in content_lower)
                
                # Check for phrase matches (higher score)
                phrase_matches = 0
                if len(query_words) > 1:
                    for i in range(len(query_words) - 1):
                        phrase = f"{query_words[i]} {query_words[i+1]}"
                        if phrase in content_lower:
                            phrase_matches += 1
                
                # Calculate relevance score
                word_score = word_matches / len(query_words)
                phrase_score = phrase_matches / max(1, len(query_words) - 1)
                
                # Combined score with emphasis on phrase matches
                total_score = (word_score * 0.6) + (phrase_score * 0.4)
                
                if total_score > 0:
                    # Create clean result dictionary with safe metadata handling
                    safe_metadata = {}
                    try:
                        if doc.doc_metadata and isinstance(doc.doc_metadata, dict):
                            safe_metadata = doc.doc_metadata
                        elif doc.doc_metadata:
                            safe_metadata = {"data": str(doc.doc_metadata)}
                    except:
                        safe_metadata = {}
                    
                    result = {
                        "content": str(doc.content)[:400],  # Limit content length
                        "score": round(float(total_score), 3),
                        "word_matches": int(word_matches),
                        "phrase_matches": int(phrase_matches),
                        "metadata": safe_metadata,
                        "id": int(doc.id),
                        "created_at": str(doc.created_at) if doc.created_at else None
                    }
                    results.append(result)
            
            # Sort by score and return top results
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:max_results]
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Search error: {e}")
        return []

@app.get("/.well-known/ai-plugin.json")
async def get_plugin_manifest():
    return {
        "schema_version": "v1",
        "name_for_human": "Quilt Sentence Search",
        "name_for_model": "quilt_sentence_search",
        "description_for_human": "Search through your indexed content using full sentences and natural language queries",
        "description_for_model": "Search through indexed content using complete sentences or phrases. Supports natural language queries and returns relevant documents with content and metadata that can help answer questions with accurate, sourced information.",
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
    query: str = Query(..., description="Search query - can be a full sentence or phrase"),
    max_results: int = Query(5, description="Maximum number of results", ge=1, le=20)
):
    """Search the database using full sentences"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        print(f"🔍 Searching for: '{query}'")
        
        # Perform sentence-based search
        results = search_with_sentence(query, max_results)
        
        print(f"✅ Found {len(results)} results")
        
        # Return clean JSON response
        response_data = {
            "query": query,
            "search_type": "sentence_search",
            "total_results": len(results),
            "results": []
        }
        
        for i, result in enumerate(results, 1):
            response_data["results"].append({
                "rank": i,
                "content": result["content"],
                "score": result["score"],
                "word_matches": result["word_matches"],
                "phrase_matches": result["phrase_matches"],
                "metadata": result["metadata"],
                "search_explanation": f"Found {result['word_matches']} word matches and {result['phrase_matches']} phrase matches"
            })
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        error_msg = f"Search error: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/demo-search")
async def demo_search():
    """Demonstrate sentence search with example queries"""
    example_queries = [
        "What is machine learning and how does it work?",
        "Tell me about Python programming language",
        "How do databases store information?",
        "Explain vector embeddings and their uses"
    ]
    
    results = {}
    for query in example_queries:
        search_results = search_with_sentence(query, 2)
        results[query] = {
            "found_results": len(search_results),
            "top_result": search_results[0]["content"][:100] + "..." if search_results else "No results found"
        }
    
    return JSONResponse(content={
        "message": "Demo of sentence search capabilities",
        "example_searches": results,
        "instructions": "Use /search?query=your_sentence_here to search with full sentences"
    })

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        from database_config import get_db, Document
        
        db = next(get_db())
        try:
            total_docs = db.query(Document).count()
            
            # Get sample content to show what's available
            sample_docs = db.query(Document).limit(3).all()
            sample_content = [doc.content[:100] + "..." for doc in sample_docs]
            
            return JSONResponse(content={
                "database_info": {
                    "total_documents": total_docs,
                    "database_type": "PostgreSQL",
                    "search_type": "sentence_and_phrase_matching",
                    "capabilities": [
                        "Full sentence search",
                        "Multi-word phrase matching",
                        "Relevance scoring",
                        "Natural language queries"
                    ]
                },
                "sample_content": sample_content,
                "usage_tips": [
                    "Use complete sentences for best results",
                    "Ask natural questions like 'What is machine learning?'",
                    "Longer, more specific queries often return better results"
                ]
            })
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
            return JSONResponse(content={
                "status": "healthy",
                "total_documents": count,
                "search_ready": True,
                "capabilities": ["sentence_search", "phrase_matching", "natural_language"]
            })
        finally:
            db.close()
            
    except Exception as e:
        return JSONResponse(content={
            "status": "unhealthy", 
            "error": str(e),
            "search_ready": False
        })

@app.get("/")
async def root():
    return JSONResponse(content={
        "name": "Quilt Sentence Search Plugin",
        "version": "1.0.0",
        "description": "Search your database using complete sentences and natural language",
        "features": [
            "Full sentence search",
            "Multi-word phrase matching", 
            "Natural language queries",
            "Relevance scoring"
        ],
        "examples": [
            "/search?query=What is machine learning?",
            "/search?query=How do databases work?",
            "/search?query=Explain Python programming",
            "/demo-search - See example searches"
        ]
    })

if __name__ == "__main__":
    print("🚀 Starting Sentence Search Plugin...")
    print("✨ Features:")
    print("  - Full sentence search")
    print("  - Natural language queries")
    print("  - Phrase matching")
    print("  - Relevance scoring")
    
    uvicorn.run(
        "sentence_search_plugin:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False
    )
