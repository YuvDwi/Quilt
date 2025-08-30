"""
LLM-Powered Search Interface
Combines your database search with LLM responses for public use
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import psycopg2
import requests
import json
import os
from typing import List, Dict, Any

app = FastAPI(
    title="AI-Powered Database Search",
    description="Search database and get AI-powered answers"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key-here")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-key-here")

def search_database(query: str, max_results: int = 5) -> List[Dict]:
    """Search your database"""
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
                "id": int(doc_id),
                "content": str(content),
                "score": round(float(score), 3),
                "metadata": dict(metadata) if metadata else {}
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        conn.close()
        return results
        
    except Exception as e:
        print(f"Database search error: {e}")
        return []

def call_openai(prompt: str, context: str) -> str:
    """Call OpenAI API"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system", 
                    "content": f"You are a helpful assistant. Use the following context from a database to answer questions. If the context doesn't contain relevant information, say so. Context: {context}"
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"OpenAI API error: {response.status_code}"
            
    except Exception as e:
        return f"Error calling OpenAI: {str(e)}"

def call_anthropic(prompt: str, context: str) -> str:
    """Call Anthropic Claude API"""
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        full_prompt = f"""Human: Based on the following database content, please answer this question: {prompt}

Database content:
{context}

If the database content doesn't contain relevant information for the question, please say so clearly.
