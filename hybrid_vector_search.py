import sqlite3
import json
import re
import math
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional

class HybridVectorSearch:
    def __init__(self):
        self.db_path = "search_data.db"
        self.documents = []
        self.word_frequencies = defaultdict(lambda: defaultdict(int))
        self.document_frequencies = defaultdict(int)
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
            cursor = conn.execute("SELECT id, content FROM documents ORDER BY id")
            for doc_id, content in cursor.fetchall():
                self.documents.append((doc_id, content))
                self._update_frequencies(content, doc_id)

    def _tokenize(self, text: str) -> List[str]:
        # Simple tokenization - split on non-alphanumeric and convert to lowercase
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return [word for word in words if len(word) > 2]  # Filter short words
    
    def _update_frequencies(self, content: str, doc_id: int):
        words = self._tokenize(content)
        word_counts = Counter(words)
        
        for word, count in word_counts.items():
            self.word_frequencies[doc_id][word] = count
            if count > 0:  # Word appears in this document
                self.document_frequencies[word] += 1

    def add_document(self, content: str, metadata: Dict = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO documents (content, metadata) VALUES (?, ?)",
                (content, json.dumps(metadata) if metadata else None)
            )
            doc_id = cursor.lastrowid
        
        self.documents.append((doc_id, content))
        self._update_frequencies(content, doc_id)

    def _calculate_tfidf_score(self, query_words: List[str], doc_id: int, content: str) -> float:
        """Calculate TF-IDF score for a document given query words"""
        if not query_words:
            return 0.0
        
        score = 0.0
        doc_word_count = sum(self.word_frequencies[doc_id].values())
        total_docs = len(self.documents)
        
        for word in query_words:
            if word in self.word_frequencies[doc_id]:
                # Term Frequency (TF)
                tf = self.word_frequencies[doc_id][word] / doc_word_count
                
                # Inverse Document Frequency (IDF)
                df = self.document_frequencies.get(word, 0)
                if df > 0:
                    idf = math.log(total_docs / df)
                else:
                    idf = 0
                
                score += tf * idf
        
        return score

    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Hybrid search combining TF-IDF and keyword matching"""
        if not self.documents:
            return []
        
        query_words = self._tokenize(query)
        if not query_words:
            return []
        
        results = []
        
        for doc_id, content in self.documents:
            # Calculate TF-IDF score
            tfidf_score = self._calculate_tfidf_score(query_words, doc_id, content)
            
            # Calculate keyword match score
            keyword_score = self._calculate_keyword_score(query_words, content)
            
            # Combined score (weighted)
            combined_score = (0.7 * tfidf_score) + (0.3 * keyword_score)
            
            if combined_score > 0:
                results.append({
                    "content": content,
                    "score": combined_score,
                    "metadata": self._get_metadata(doc_id),
                    "search_type": "hybrid"
                })
        
        # Sort by score and return top k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]

    def _calculate_keyword_score(self, query_words: List[str], content: str) -> float:
        """Simple keyword matching score"""
        content_lower = content.lower()
        matches = sum(1 for word in query_words if word in content_lower)
        return matches / len(query_words) if query_words else 0

    def keyword_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Simple keyword-based search"""
        if not self.documents:
            return []
        
        query_words = self._tokenize(query)
        results = []
        
        for doc_id, content in self.documents:
            score = self._calculate_keyword_score(query_words, content)
            if score > 0:
                results.append({
                    "content": content,
                    "score": score,
                    "metadata": self._get_metadata(doc_id),
                    "search_type": "keyword"
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]

    def vector_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """TF-IDF vector search (lightweight implementation)"""
        return self.search_similar(query, k)

    def _get_metadata(self, doc_id: int) -> Dict:
        """Get metadata for a document"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT metadata FROM documents WHERE id = ?", (doc_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    return json.loads(row[0])
        except:
            pass
        return {}

    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        return {
            "total_documents": len(self.documents),
            "unique_words": len(self.document_frequencies),
            "database_path": self.db_path
        }