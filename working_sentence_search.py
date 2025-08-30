"""
Simple working sentence search using direct SQL
Avoids SQLAlchemy object issues by using raw SQL
"""

from fastapi import FastAPI, HTTPException, Query, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Working Sentence Search",
    description="Search with full sentences using direct SQL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Get direct PostgreSQL connection"""
    try:
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://quilt_user:your_secure_password@localhost:5432/quilt_embeddings"
        )
        
        # Parse the URL for psycopg2
        if DATABASE_URL.startswith("postgresql://"):
            # Convert to psycopg2 format
            url_parts = DATABASE_URL.replace("postgresql://", "").split("/")
            db_name = url_parts[1] if len(url_parts) > 1 else "quilt_embeddings"
            user_host = url_parts[0].split("@")
            if len(user_host) == 2:
                user_pass = user_host[0].split(":")
                user = user_pass[0]
                password = user_pass[1] if len(user_pass) > 1 else ""
                host_port = user_host[1].split(":")
                host = host_port[0]
                port = host_port[1] if len(host_port) > 1 else "5432"
            else:
                user, password, host, port = "quilt_user", "your_secure_password", "localhost", "5432"
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=db_name,
            user=user,
            password=password
        )
        return conn
        
    except Exception as e:
        print(f"DB connection error: {e}")
        return None

def search_with_sentence(query: str, max_results: int = 5):
    """Search using full sentences with direct SQL"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Split query into words for matching
        query_words = [word.lower().strip() for word in query.split() if len(word.strip()) > 2]
        
        if not query_words:
            return []
        
        # Build SQL query for text search
        # Use PostgreSQL's ILIKE for case-insensitive matching
        conditions = []
        params = []
        
        for word in query_words:
            conditions.append("LOWER(content) LIKE %s")
            params.append(f"%{word}%")
        
        # Combine with OR to find documents with any matching words
        where_clause = " OR ".join(conditions)
        
        sql = f"""
        SELECT id, content, doc_metadata, created_at
        FROM documents 
        WHERE {where_clause}
        ORDER BY id
        LIMIT %s
        """
        
        params.append(max_results * 2)  # Get more results for scoring
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # Score the results
        results = []
        for row in rows:
            doc_id, content, metadata_json, created_at = row
            
            content_lower = content.lower()
            
            # Count word matches
            word_matches = sum(1 for word in query_words if word in content_lower)
            
            # Count phrase matches
            phrase_matches = 0
            if len(query_words) > 1:
                for i in range(len(query_words) - 1):
                    phrase = f"{query_words[i]} {query_words[i+1]}"
                    if phrase in content_lower:
                        phrase_matches += 1
            
            # Calculate score
            word_score = word_matches / len(query_words)
            phrase_score = phrase_matches / max(1, len(query_words) - 1) if len(query_words) > 1 else 0
            total_score = (word_score * 0.6) + (phrase_score * 0.4)
            
            if total_score > 0:
                # Parse metadata safely
                safe_metadata = {}
                if metadata_json:
                    try:
                        if isinstance(metadata_json, dict):
                            safe_metadata = metadata_json
                        else:
                            safe_metadata = {"data": str(metadata_json)}
                    except:
                        safe_metadata = {}
                
                result = {
                    "content": content[:400],
                    "score": round(total_score, 3),
                    "word_matches": word_matches,
                    "phrase_matches": phrase_matches,
                    "metadata": safe_metadata,
                    "id": doc_id,
                    "created_at": str(created_at) if created_at else None
                }
                results.append(result)
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
        
    except Exception as e:
        print(f"Search error: {e}")
        return []
    finally:
        conn.close()

@app.get("/.well-known/ai-plugin.json")
async def get_plugin_manifest():
    return {
        "schema_version": "v1",
        "name_for_human": "Quilt Sentence Search",
        "name_for_model": "quilt_sentence_search",
        "description_for_human": "Search through your indexed content using full sentences and natural language queries",
        "description_for_model": "Search indexed content using complete sentences, phrases, or natural language questions. Returns relevant documents with content and metadata for answering questions.",
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
    query: str = Query(..., description="Search query - use full sentences for best results"),
    max_results: int = Query(5, description="Maximum number of results", ge=1, le=10)
):
    """Search using complete sentences or phrases"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        print(f"🔍 Sentence search: '{query}'")
        
        results = search_with_sentence(query, max_results)
        
        print(f"✅ Found {len(results)} results")
        
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
                "score": result["score"],
                "word_matches": result["word_matches"],
                "phrase_matches": result["phrase_matches"],
                "metadata": result["metadata"],
                "explanation": f"Matched {result['word_matches']} words and {result['phrase_matches']} phrases from your query"
            })
        
        return JSONResponse(content=response)
        
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/demo")
async def demo_searches():
    """Demo various sentence searches"""
    examples = [
        "What is machine learning?",
        "How does Python programming work?", 
        "Tell me about databases and PostgreSQL",
        "Explain vector embeddings"
    ]
    
    demo_results = {}
    for query in examples:
        results = search_with_sentence(query, 2)
        demo_results[query] = {
            "results_found": len(results),
            "best_match": results[0]["content"][:150] + "..." if results else "No matches found",
            "score": results[0]["score"] if results else 0
        }
    
    return JSONResponse(content={
        "message": "Demo of sentence search capabilities",
        "examples": demo_results,
        "instructions": "Use /search?query=your_full_sentence_here for best results"
    })

@app.get("/health")
async def health_check():
    """Check if database is accessible"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            conn.close()
            
            return JSONResponse(content={
                "status": "healthy",
                "database_connected": True,
                "total_documents": count,
                "search_ready": True
            })
        else:
            return JSONResponse(content={
                "status": "unhealthy",
                "database_connected": False,
                "search_ready": False
            })
            
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "error": str(e),
            "search_ready": False
        })

@app.get("/")
async def root():
    return JSONResponse(content={
        "name": "Working Sentence Search Plugin",
        "version": "1.0.0",
        "description": "Search your database using complete sentences and questions",
        "examples": [
            "What is machine learning?",
            "How do databases work?",
            "Tell me about Python programming",
            "Explain vector embeddings and AI"
        ],
        "endpoints": {
            "search": "/search?query=your_question_here",
            "demo": "/demo - See example searches",
            "health": "/health - Check system status"
        }
    })

if __name__ == "__main__":
    print("🚀 Starting Working Sentence Search Plugin...")
    print("✨ Ready to search with:")
    print("  - Complete sentences")
    print("  - Natural language questions") 
    print("  - Multi-word phrases")
    print("  - Conversational queries")
    
    uvicorn.run(
        "working_sentence_search:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
