import sqlite3
import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any, Optional

class HybridVectorSearch:
    def __init__(self):
        self.db_path = "search_data.db"
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.vectors = None
        self.documents = []
        self.init_database()
        self._load_existing_documents()

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content ON documents(content)")

    def _load_existing_documents(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT content FROM documents ORDER BY id")
            self.documents = [row[0] for row in cursor.fetchall()]
            if self.documents:
                self._rebuild_vectors()

    def _rebuild_vectors(self):
        if len(self.documents) > 0:
            try:
                self.vectors = self.vectorizer.fit_transform(self.documents)
            except Exception as e:
                print(f"Error building vectors: {e}")
                self.vectors = None

    def add_document(self, content: str, metadata: Dict = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO documents (content, metadata) VALUES (?, ?)",
                (content, json.dumps(metadata) if metadata else None)
            )
        
        self.documents.append(content)
        
        # Rebuild vectors every 10 documents for efficiency
        if len(self.documents) % 10 == 0:
            self._rebuild_vectors()

    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
        
        if self.vectors is None:
            self._rebuild_vectors()
        
        if self.vectors is not None:
            try:
                # Vector similarity search
                query_vector = self.vectorizer.transform([query])
                similarities = np.dot(self.vectors, query_vector.T).toarray().flatten()
                
                # Get top results
                top_indices = np.argsort(similarities)[-k:][::-1]
                
                results = []
                for i in top_indices:
                    if similarities[i] > 0.01:  # Minimum similarity threshold
                        results.append({
                            "content": self.documents[i],
                            "score": float(similarities[i]),
                            "metadata": self._get_metadata(i),
                            "search_type": "vector"
                        })
                
                # If vector search returns results, use them
                if results:
                    return results[:k]
                    
            except Exception as e:
                print(f"Vector search failed: {e}")
        
        # Fall back to keyword search
        return self.keyword_search(query, k)

    def keyword_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        query_words = re.findall(r'\w+', query.lower())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build search conditions for each word
            conditions = []
            params = []
            for word in query_words:
                if len(word) > 2:  # Only search for words longer than 2 chars
                    conditions.append("LOWER(content) LIKE ?")
                    params.append(f"%{word}%")
            
            if not conditions:
                return []
            
            query_sql = f"""
                SELECT content, metadata
                FROM documents 
                WHERE {' AND '.join(conditions)}
                LIMIT ?
            """
            params.append(k)
            
            cursor.execute(query_sql, params)
            results = cursor.fetchall()
            
            return [
                {
                    "content": row[0],
                    "metadata": json.loads(row[1]) if row[1] else {},
                    "score": 1.0,
                    "search_type": "keyword"
                }
                for row in results
            ]

    def hybrid_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # Get both vector and keyword results
        vector_results = self.search_similar(query, k // 2 + 1)
        keyword_results = self.keyword_search(query, k // 2 + 1)
        
        # Combine and deduplicate
        seen_content = set()
        combined_results = []
        
        for result in vector_results + keyword_results:
            content_hash = hash(result["content"])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                combined_results.append(result)
        
        return combined_results[:k]

    def _get_metadata(self, doc_index: int) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT metadata FROM documents WHERE id = ?", 
                (doc_index + 1,)
            )
            row = cursor.fetchone()
            return json.loads(row[0]) if row and row[0] else {}

    def list_documents(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT content, metadata FROM documents")
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    "content": row[0],
                    "metadata": json.loads(row[1]) if row[1] else {}
                })
            
            return {
                "documents": documents,
                "total_count": len(documents),
                "vectorized": self.vectors is not None
            }
