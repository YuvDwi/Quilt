"""
Final Working ChatGPT Plugin - Sentence Search
Handles full sentences, questions, and natural language queries
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import psycopg2
import json

app = FastAPI(
    title="Quilt Sentence Search Plugin",
    description="Search using complete sentences and natural language",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    """Get database connection"""
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="quilt_embeddings",
        user="quilt_user",
        password="your_secure_password"
    )

def sentence_search(query: str, max_results: int = 5):
    """Search with full sentences"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Extract meaningful words from the sentence
        words = [w.lower().strip() for w in query.split() if len(w.strip()) > 2]
        
        if not words:
            return []
        
        # Build search query - look for documents containing any of the words
        conditions = []
        params = []
        for word in words:
            conditions.append("LOWER(content) LIKE %s")
            params.append(f"%{word}%")
        
        where_clause = " OR ".join(conditions)
        sql = f"""
            SELECT id, content, doc_metadata 
            FROM documents 
            WHERE {where_clause}
            ORDER BY id
            LIMIT %s
        """
        params.append(max_results * 2)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # Score and rank results
        results = []
        for row in rows:
            doc_id, content, metadata = row
            content_lower = content.lower()
            
            # Count word matches
            word_matches = sum(1 for word in words if word in content_lower)
            
            # Count phrase matches (consecutive words)
            phrase_matches = 0
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                if phrase in content_lower:
                    phrase_matches += 1
            
            # Calculate relevance score
            word_score = word_matches / len(words)
            phrase_bonus = phrase_matches * 0.3
            total_score = word_score + phrase_bonus
            
            if total_score > 0:
                # Safely handle metadata
                safe_metadata = {}
                if metadata and isinstance(metadata, dict):
                    safe_metadata = metadata
                
                result = {
                    "content": content[:400],
                    "score": round(total_score, 3),
                    "word_matches": word_matches,
                    "phrase_matches": phrase_matches,
                    "metadata": safe_metadata,
                    "doc_id": doc_id
                }
                results.append(result)
        
        # Sort by score (best matches first)
        results.sort(key=lambda x: x["score"], reverse=True)
        conn.close()
        
        return results[:max_results]
        
    except Exception as e:
        print(f"Search error: {e}")
        return []

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    return {
        "schema_version": "v1",
        "name_for_human": "Quilt Sentence Search",
        "name_for_model": "quilt_sentence_search",
        "description_for_human": "Search your database using complete sentences, questions, and natural language",
        "description_for_model": "Search through indexed content using full sentences, questions, or natural language queries. Perfect for finding information to answer user questions with accurate, sourced data.",
        "auth": {"type": "none"},
        "api": {
            "type": "openapi",
            "url": "http://localhost:8000/openapi.json"
        }
    }

@app.get("/search")
async def search_content(
    query: str = Query(..., description="Your search query - use complete sentences for best results"),
    max_results: int = Query(5, description="Maximum results to return", ge=1, le=10)
):
    """Search using complete sentences or natural language questions"""
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    print(f"🔍 Searching: '{query}'")
    
    try:
        results = sentence_search(query, max_results)
        
        response = {
            "query": query,
            "search_type": "sentence_search",
            "total_results": len(results),
            "results": []
        }
        
        for i, result in enumerate(results, 1):
            response["results"].append({
                "rank": i,
                "content": result["content"],
                "relevance_score": result["score"],
                "word_matches": result["word_matches"],
                "phrase_matches": result["phrase_matches"],
                "metadata": result["metadata"],
                "explanation": f"Found {result['word_matches']} matching words and {result['phrase_matches']} matching phrases"
            })
        
        print(f"✅ Returned {len(results)} results")
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/examples")
async def search_examples():
    """Show example sentence searches"""
    examples = [
        "What is machine learning?",
        "How does Python programming work?",
        "Tell me about databases and PostgreSQL",
        "Explain vector embeddings and their uses",
        "What are the benefits of artificial intelligence?"
    ]
    
    example_results = {}
    for example in examples:
        results = sentence_search(example, 2)
        example_results[example] = {
            "results_found": len(results),
            "best_match_preview": results[0]["content"][:100] + "..." if results else "No matches",
            "relevance_score": results[0]["score"] if results else 0
        }
    
    return {
        "message": "Example sentence searches",
        "examples": example_results,
        "usage_tip": "Ask natural questions or use descriptive sentences for best results"
    }

@app.get("/health")
async def health_check():
    """Health check"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "total_documents": count,
            "search_ready": True,
            "supports": ["sentence_search", "natural_language", "questions"]
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "search_ready": False
        }

@app.get("/")
async def root():
    return {
        "name": "Quilt Sentence Search Plugin",
        "description": "Search your database using complete sentences and natural language",
        "capabilities": [
            "Full sentence search",
            "Natural language questions",
            "Multi-word phrase matching",
            "Relevance scoring"
        ],
        "example_queries": [
            "What is machine learning?",
            "How do databases work?",
            "Tell me about Python programming",
            "Explain artificial intelligence"
        ],
        "usage": "Use /search?query=your_complete_sentence_here"
    }

if __name__ == "__main__":
    print("🚀 Final Working Sentence Search Plugin")
    print("✨ Features:")
    print("  ✅ Complete sentence search")
    print("  ✅ Natural language questions") 
    print("  ✅ Multi-word phrase matching")
    print("  ✅ Relevance scoring")
    print("  ✅ ChatGPT integration ready")
    
    uvicorn.run("final_working_plugin:app", host="0.0.0.0", port=8000)
