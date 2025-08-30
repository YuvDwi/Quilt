#!/usr/bin/env python3
"""
HTTP MCP Server for Cloud Deployment
Simple HTTP endpoint that ChatGPT Desktop can connect to
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
import uvicorn
from typing import Dict, List
import json

app = FastAPI(
    title="MCP Database Server",
    description="HTTP MCP server for database search"
)

# Add CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "quilt_embeddings"),
    "user": os.getenv("DB_USER", "quilt_user"),
    "password": os.getenv("DB_PASSWORD", "your_secure_password")
}

def search_database(query: str, max_results: int = 5) -> List[Dict]:
    """Search the database directly"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        words = [w.strip().lower() for w in query.split() if len(w.strip()) > 2]
        if not words:
            return []
        
        conditions = []
        params = []
        for word in words:
            conditions.append("LOWER(content) LIKE %s")
            params.append(f"%{word}%")
        
        where_clause = " OR ".join(conditions)
        sql = f"SELECT id, content, doc_metadata FROM documents WHERE {where_clause} LIMIT %s"
        params.append(max_results)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            doc_id, content, metadata = row
            results.append({
                "id": int(doc_id),
                "content": str(content),
                "metadata": dict(metadata) if metadata else {}
            })
        
        return results
        
    except Exception as e:
        print(f"Database error: {e}")
        return []

@app.get("/")
async def root():
    return {
        "name": "MCP Database Server",
        "status": "running",
        "endpoints": {
            "search": "/search?query=your_query",
            "mcp_manifest": "/.well-known/ai-plugin.json",
            "health": "/health"
        }
    }

@app.get("/search")
async def search_endpoint(query: str, max_results: int = 5):
    """Direct search endpoint"""
    try:
        results = search_database(query, max_results)
        return {
            "query": query,
            "found": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "documents": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# MCP Protocol Endpoints
@app.get("/.well-known/ai-plugin.json")
async def mcp_manifest():
    """MCP manifest for ChatGPT Desktop"""
    return {
        "schema_version": "v1",
        "name_for_human": "Database Search",
        "name_for_model": "database_search",
        "description_for_human": "Search your PostgreSQL database",
        "description_for_model": "Search a PostgreSQL database for relevant content",
        "auth": {"type": "none"},
        "api": {
            "type": "openapi",
            "url": f"{os.getenv('BASE_URL', 'http://localhost:8000')}/openapi.json"
        },
        "contact_email": "support@example.com"
    }

@app.post("/mcp/tools/list")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "search_database",
                "description": "Search the PostgreSQL database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "default": 5}
                    },
                    "required": ["query"]
                }
            }
        ]
    }

@app.post("/mcp/tools/call")
async def call_tool(tool_request: Dict):
    """Call an MCP tool"""
    try:
        tool_name = tool_request.get("name")
        arguments = tool_request.get("arguments", {})
        
        if tool_name == "search_database":
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 5)
            
            results = search_database(query, max_results)
            
            if not results:
                content = f"No results found for query: '{query}'"
            else:
                content = f"Found {len(results)} results for '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    content += f"{i}. {result['content'][:300]}...\n\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": content
                    }
                ]
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting HTTP MCP Server...")
    print("📊 Database search available at: http://localhost:8000/search")
    print("🔧 MCP endpoints at: http://localhost:8000/mcp/")
    print("❤️  Health check at: http://localhost:8000/health")
    
    uvicorn.run(
        "http_mcp_server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )
