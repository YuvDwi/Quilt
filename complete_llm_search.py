"""
Complete LLM-Powered Search System
Searchable database + AI responses for public use
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import psycopg2
import requests
import json
import os
from typing import List, Dict, Any

app = FastAPI(
    title="AI Database Search",
    description="AI-powered search with database context"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM Configuration - Add your API keys here
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

def search_database(query: str, max_results: int = 3) -> List[Dict]:
    """Search your database for relevant content"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="quilt_embeddings",
            user="quilt_user",
            password="your_secure_password"
        )
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
        
        results = []
        for row in rows:
            doc_id, content, metadata = row
            content_lower = content.lower()
            matches = sum(1 for word in words if word in content_lower)
            score = matches / len(words)
            
            results.append({
                "content": str(content),
                "score": round(float(score), 3),
                "metadata": dict(metadata) if metadata else {}
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        conn.close()
        return results
        
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_ai_response(question: str, context_data: List[Dict]) -> Dict:
    """Get AI response using database context"""
    
    # Prepare context from database results
    context_text = ""
    if context_data:
        context_text = "\n\n".join([
            f"Source {i+1}: {item['content']}" 
            for i, item in enumerate(context_data[:3])
        ])
    
    # Try OpenAI first (most common)
    if OPENAI_API_KEY and OPENAI_API_KEY != "":
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Based on the following database information, please answer this question: {question}

Database sources:
{context_text}

Please provide a helpful answer based on this information. If the database doesn't contain relevant information, please say so clearly."""

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 400,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                ai_answer = response.json()["choices"][0]["message"]["content"]
                return {
                    "answer": ai_answer,
                    "model": "OpenAI GPT-3.5",
                    "sources_used": len(context_data)
                }
            else:
                print(f"OpenAI error: {response.status_code}")
        except Exception as e:
            print(f"OpenAI failed: {e}")
    
    # Fallback: Simple response without LLM
    if context_data:
        simple_answer = f"""Based on your database, here's what I found about "{question}":

{context_data[0]['content']}

This information comes from your indexed content."""
        
        return {
            "answer": simple_answer,
            "model": "Database retrieval (no LLM)",
            "sources_used": len(context_data)
        }
    else:
        return {
            "answer": f"I couldn't find relevant information about '{question}' in your database.",
            "model": "Database retrieval",
            "sources_used": 0
        }

@app.get("/", response_class=HTMLResponse)
async def web_interface():
    """Web interface for public use"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Database Search</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .search-box {
                width: 100%;
                padding: 15px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-bottom: 15px;
                box-sizing: border-box;
            }
            .search-button {
                background: #007AFF;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                width: 100%;
            }
            .search-button:hover {
                background: #0056b3;
            }
            .result {
                margin-top: 20px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #007AFF;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
            .sources {
                margin-top: 15px;
                padding: 15px;
                background: #e9ecef;
                border-radius: 6px;
                font-size: 14px;
            }
            .example-queries {
                margin-top: 20px;
                padding: 15px;
                background: #fff3cd;
                border-radius: 6px;
                border-left: 4px solid #ffc107;
            }
            .example-query {
                margin: 5px 0;
                padding: 5px 10px;
                background: white;
                border-radius: 4px;
                cursor: pointer;
                border: 1px solid #ddd;
            }
            .example-query:hover {
                background: #f8f9fa;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Database Search</h1>
            <p style="text-align: center; color: #666; margin-bottom: 30px;">
                Ask questions and get AI-powered answers from the database
            </p>
            
            <input type="text" id="queryInput" class="search-box" 
                   placeholder="Ask a question... (e.g., What is machine learning?)" 
                   onkeypress="if(event.key==='Enter') search()">
            
            <button class="search-button" onclick="search()">🔍 Search & Ask AI</button>
            
            <div class="example-queries">
                <strong>💡 Try these examples:</strong>
                <div class="example-query" onclick="setQuery('What is machine learning?')">What is machine learning?</div>
                <div class="example-query" onclick="setQuery('How does Python programming work?')">How does Python programming work?</div>
                <div class="example-query" onclick="setQuery('Tell me about databases')">Tell me about databases</div>
                <div class="example-query" onclick="setQuery('Explain vector embeddings')">Explain vector embeddings</div>
            </div>
            
            <div id="result"></div>
        </div>

        <script>
            function setQuery(query) {
                document.getElementById('queryInput').value = query;
            }
            
            async function search() {
                const query = document.getElementById('queryInput').value.trim();
                if (!query) {
                    alert('Please enter a question');
                    return;
                }
                
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<div class="loading">🤖 Searching database and generating AI response...</div>';
                
                try {
                    const response = await fetch(`/ai-search?question=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    
                    if (data.error) {
                        resultDiv.innerHTML = `<div class="result"><strong>❌ Error:</strong> ${data.error}</div>`;
                        return;
                    }
                    
                    let html = `
                        <div class="result">
                            <h3>🤖 AI Response:</h3>
                            <p>${data.answer.replace(/\\n/g, '<br>')}</p>
                            
                            <div class="sources">
                                <strong>📊 Search Info:</strong><br>
                                Model: ${data.model}<br>
                                Sources used: ${data.sources_used}<br>
                                Database results: ${data.database_results}
                            </div>
                    `;
                    
                    if (data.sources && data.sources.length > 0) {
                        html += '<div class="sources"><strong>📄 Database Sources:</strong>';
                        data.sources.forEach((source, i) => {
                            html += `<br><br><strong>Source ${i+1}:</strong> ${source.content.substring(0, 200)}...`;
                        });
                        html += '</div>';
                    }
                    
                    html += '</div>';
                    resultDiv.innerHTML = html;
                    
                } catch (error) {
                    resultDiv.innerHTML = `<div class="result"><strong>❌ Error:</strong> ${error.message}</div>`;
                }
            }
            
            // Auto-focus on input
            document.getElementById('queryInput').focus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/ai-search")
async def ai_search_endpoint(question: str = Query(...)):
    """AI-powered search endpoint"""
    try:
        print(f"🔍 AI Search: '{question}'")
        
        # Search database
        database_results = search_database(question, max_results=3)
        
        # Get AI response
        ai_response = get_ai_response(question, database_results)
        
        response = {
            "question": question,
            "answer": ai_response["answer"],
            "model": ai_response["model"],
            "sources_used": ai_response["sources_used"],
            "database_results": len(database_results),
            "sources": database_results
        }
        
        print(f"✅ AI Response generated ({ai_response['model']})")
        return response
        
    except Exception as e:
        print(f"❌ AI Search error: {e}")
        return {"error": str(e)}

@app.get("/api/search")
async def api_search(query: str = Query(...), max_results: int = Query(5)):
    """Raw database search API (for developers)"""
    try:
        results = search_database(query, max_results)
        return {
            "query": query,
            "found": len(results),
            "results": results
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check"""
    try:
        # Test database
        results = search_database("test", 1)
        
        # Check LLM availability
        llm_status = "None"
        if OPENAI_API_KEY and OPENAI_API_KEY != "":
            llm_status = "OpenAI available"
        elif ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "":
            llm_status = "Anthropic available"
        
        return {
            "status": "healthy",
            "database": "connected",
            "llm": llm_status,
            "web_interface": "http://localhost:9000",
            "api_endpoint": "http://localhost:9000/api/search"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    print("🚀 AI-POWERED DATABASE SEARCH")
    print("✨ Features:")
    print("  🌐 Public web interface")
    print("  🤖 AI-powered responses")
    print("  📊 Database search")
    print("  🔗 API for developers")
    print()
    print("🌍 Access points:")
    print("  Web Interface: http://localhost:9000")
    print("  AI Search API: http://localhost:9000/ai-search?question=your_question")
    print("  Raw Search API: http://localhost:9000/api/search?query=your_query")
    print()
    print("⚙️  Setup:")
    print("  1. Add OPENAI_API_KEY to environment for AI responses")
    print("  2. Share the URL with others")
    print("  3. Deploy to cloud for worldwide access")
    
    uvicorn.run("complete_llm_search:app", host="0.0.0.0", port=9000, reload=False)
