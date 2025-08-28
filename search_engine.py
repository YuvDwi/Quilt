from fastapi import FastAPI, Query
from pydantic import BaseModel
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import re
from typing import List, Dict, Any
import sqlite3
import json

class SearchEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384
        self.index = faiss.IndexFlatIP(self.dimension)
        self.db_path = "search_data.db"
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding BLOB,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content ON documents(content)")
    
    def add_document(self, content: str, metadata: Dict = None):
        embedding = self.model.encode(content)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO documents (content, embedding, metadata) VALUES (?, ?, ?)",
                (content, embedding.tobytes(), json.dumps(metadata) if metadata else None)
            )
    
    def search_similar(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        query_text = query_text.replace("\n", " ").strip()
        query_vector = self.model.encode(query_text)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT content, embedding, metadata FROM documents")
            results = []
            
            for row in cursor.fetchall():
                content, embedding_bytes, metadata = row
                stored_vector = np.frombuffer(embedding_bytes, dtype=np.float32)
                
                similarity = np.dot(query_vector, stored_vector)
                results.append({
                    'content': content,
                    'similarity_score': float(similarity),
                    'metadata': json.loads(metadata) if metadata else {}
                })
        
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:k]
    
    def hybrid_search(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        query_text = query_text.replace("\n", " ").strip().lower()
        keywords = re.findall(r'\b\w+\b', query_text)
        vector_results = self.search_similar(query_text, k=k*2)
        
        scored_results = []
        for result in vector_results:
            content_lower = result['content'].lower()
            
            keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
            keyword_score = keyword_matches / len(keywords) if keywords else 0
            
            phrase_bonus = 0.3 if query_text in content_lower else 0
            
            order_bonus = 0
            if len(keywords) > 1:
                for i in range(len(keywords) - 1):
                    if keywords[i] + " " + keywords[i + 1] in content_lower:
                        order_bonus += 0.1
            
            hybrid_score = (result['similarity_score'] * 0.6 + 
                           keyword_score * 0.3 + 
                           phrase_bonus + 
                           order_bonus)
            
            scored_results.append({
                **result,
                'keyword_score': keyword_score,
                'phrase_bonus': phrase_bonus,
                'order_bonus': order_bonus,
                'hybrid_score': hybrid_score
            })
        
        scored_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        final_results = []
        for i, result in enumerate(scored_results[:k]):
            final_results.append({
                "rank": i + 1,
                "content": result['content'],
                "similarity_score": result['similarity_score'],
                "hybrid_score": round(result['hybrid_score'], 3),
                "keyword_matches": result['keyword_score'],
                "exact_phrase": bool(result['phrase_bonus'] > 0),
                "metadata": result['metadata']
            })
        
        return final_results

search_engine = SearchEngine()

app = FastAPI()

@app.post("/documents/")
async def add_document(content: str, metadata: Dict = None):
    search_engine.add_document(content, metadata)
    return {"message": "Document added successfully"}

@app.get("/search/")
async def search_endpoint(q: str = Query(..., description="Search query")):
    results = search_engine.hybrid_search(q)
    return {"query": q, "results": results}

@app.get("/search/vector/")
async def vector_search_endpoint(q: str = Query(..., description="Vector search query")):
    results = search_engine.search_similar(q)
    return {"query": q, "results": results, "method": "vector_only"}

@app.get("/search/hybrid/")
async def hybrid_search_endpoint(q: str = Query(..., description="Hybrid search query")):
    results = search_engine.hybrid_search(q)
    return {"query": q, "results": results, "method": "hybrid"}

@app.get("/documents/")
async def list_documents():
    with sqlite3.connect(search_engine.db_path) as conn:
        cursor = conn.execute("SELECT id, content, metadata, created_at FROM documents")
        documents = []
        for row in cursor.fetchall():
            documents.append({
                "id": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]) if row[2] else {},
                "created_at": row[3]
            })
        return {"documents": documents}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
