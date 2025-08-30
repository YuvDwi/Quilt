"""
Local Network Sharing Version
Allows others on your network to access the search
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import psycopg2
import socket

app = FastAPI(title="Shared Database Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def search_db(query_text: str, limit: int = 5):
    """Database search function"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="quilt_embeddings",
            user="quilt_user",
            password="your_secure_password"
        )
        cursor = conn.cursor()
        
        words = [w.strip().lower() for w in query_text.split() if len(w.strip()) > 2]
        if not words:
            return []
        
        conditions = []
        params = []
        for word in words:
            conditions.append("LOWER(content) LIKE %s")
            params.append(f"%{word}%")
        
        where_clause = " OR ".join(conditions)
        sql = f"SELECT id, content, doc_metadata FROM documents WHERE {where_clause} LIMIT %s"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            doc_id, content, metadata = row
            content_lower = content.lower()
            matches = sum(1 for word in words if word in content_lower)
            score = matches / len(words)
            
            result = {
                "id": int(doc_id),
                "content": str(content)[:400],
                "score": round(float(score), 3),
                "matches": int(matches),
                "metadata": dict(metadata) if metadata else {}
            }
            results.append(result)
        
        results.sort(key=lambda x: x["score"], reverse=True)
        conn.close()
        return results
        
    except Exception as e:
        print(f"Search error: {e}")
        return []

@app.get("/search")
def search(query: str = Query(...), max_results: int = Query(5)):
    """Public search endpoint"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query required")
    
    print(f"🔍 Search from network: '{query}'")
    
    try:
        results = search_db(query, max_results)
        
        response = {
            "query": query,
            "found": len(results),
            "results": []
        }
        
        for i, result in enumerate(results, 1):
            response["results"].append({
                "rank": i,
                "content": result["content"],
                "relevance": result["score"],
                "word_matches": result["matches"],
                "metadata": result["metadata"]
            })
        
        print(f"✅ Returned {len(results)} results to network user")
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    # Get local IP address
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "your-local-ip"
    
    return {
        "name": "Shared Database Search",
        "status": "PUBLIC",
        "access": f"Available on your network at http://{local_ip}:9000",
        "usage": "Anyone on your network can search using /search?query=...",
        "example": f"http://{local_ip}:9000/search?query=machine%20learning"
    }

def get_local_ip():
    """Get local network IP"""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

if __name__ == "__main__":
    local_ip = get_local_ip()
    
    print("🌐 SHARED DATABASE SEARCH")
    print("🔓 Now accessible to others on your network!")
    print(f"📍 Local access: http://localhost:9000")
    print(f"🌍 Network access: http://{local_ip}:9000")
    print(f"🔗 Share this URL: http://{local_ip}:9000/search?query=your_question")
    print("⚠️  Others on your WiFi/network can now search your database")
    
    uvicorn.run("local_sharing_plugin:app", host="0.0.0.0", port=9000, reload=False)
