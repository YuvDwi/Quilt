import sqlite3
import json
import re
from typing import List, Dict, Any, Optional

class LightweightSearchEngine:
    def __init__(self):
        self.db_path = "search_data.db"
        self.init_database()

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

    def add_document(self, content: str, metadata: Dict = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO documents (content, metadata) VALUES (?, ?)",
                (content, json.dumps(metadata) if metadata else None)
            )

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # Simple keyword-based search for now
        return self.keyword_search(query, top_k)
    
    def keyword_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_words = re.findall(r'\w+', query.lower())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build search conditions for each word
            conditions = []
            params = []
            for word in query_words:
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
            params.append(top_k)
            
            cursor.execute(query_sql, params)
            results = cursor.fetchall()
            
            return [
                {
                    "content": row[0],
                    "metadata": json.loads(row[1]) if row[1] else {},
                    "score": 1.0  # Simple scoring
                }
                for row in results
            ]

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # For now, just use keyword search
        return self.keyword_search(query, top_k)
