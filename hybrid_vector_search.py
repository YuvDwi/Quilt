import sqlite3
import json
import re
import math
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional

# Import Cohere embeddings only when needed
def get_cohere_embeddings():
    from cohere_embeddings import CohereEmbeddings
    return CohereEmbeddings()

class HybridVectorSearch:
    def __init__(self):
        self.db_path = "search_data.db"
        self.documents = []
        self.word_frequencies = defaultdict(lambda: defaultdict(int))
        self.document_frequencies = defaultdict(int)
        
        # Initialize Cohere embeddings lazily
        self.embedding_model = None
        
        self.init_database()
        self._load_existing_documents()
    
    def get_embedding_model(self):
        """Lazy initialization of Cohere embeddings"""
        if self.embedding_model is None:
            try:
                self.embedding_model = get_cohere_embeddings()
                print("✅ Cohere embeddings initialized")
            except Exception as e:
                print(f"⚠️ Cohere initialization failed: {e}")
                # Create dummy embeddings for fallback
                class DummyEmbeddings:
                    def encode(self, text):
                        return None
                    def encode_query(self, text):
                        return None
                self.embedding_model = DummyEmbeddings()
        return self.embedding_model

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

    def _load_existing_documents(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, content FROM documents ORDER BY id")
            for doc_id, content in cursor.fetchall():
                self.documents.append((doc_id, content))
                self._update_frequencies(content, doc_id)

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return [word for word in words if len(word) > 2]
    
    def _update_frequencies(self, content: str, doc_id: int):
        words = self._tokenize(content)
        word_counts = Counter(words)
        
        for word, count in word_counts.items():
            self.word_frequencies[doc_id][word] = count
            if count > 0:
                self.document_frequencies[word] += 1

    def add_document(self, content: str, metadata: Dict = None):
        # Generate Cohere embedding
        embedding_blob = None
        try:
            embedding_model = self.get_embedding_model()
            embedding = embedding_model.encode(content)
            if embedding is not None:
                embedding_blob = embedding.tobytes()
        except Exception as e:
            print(f"⚠️ Failed to generate embedding: {e}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO documents (content, embedding, metadata) VALUES (?, ?, ?)",
                (content, embedding_blob, json.dumps(metadata) if metadata else None)
            )
            doc_id = cursor.lastrowid
        
        self.documents.append((doc_id, content))
        self._update_frequencies(content, doc_id)

    def _calculate_tfidf_score(self, query_words: List[str], doc_id: int, content: str) -> float:
        if not query_words:
            return 0.0
        
        score = 0.0
        doc_word_count = sum(self.word_frequencies[doc_id].values())
        total_docs = len(self.documents)
        
        for word in query_words:
            if word in self.word_frequencies[doc_id]:
                tf = self.word_frequencies[doc_id][word] / doc_word_count
                df = self.document_frequencies.get(word, 0)
                if df > 0:
                    idf = math.log(total_docs / df)
                else:
                    idf = 0
                score += tf * idf
        
        return score

    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Advanced hybrid search: Cohere embeddings + TF-IDF + keywords"""
        if not self.documents:
            return []
        
        # Use Cohere embeddings if available
        embedding_model = self.get_embedding_model()
        if embedding_model.client:
            return self._hybrid_embedding_search(query, k)
        
        # Fall back to TF-IDF + keyword hybrid
        return self._tfidf_keyword_search(query, k)

    def _hybrid_embedding_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Ultimate hybrid search using Cohere embeddings"""
        try:
            embedding_model = self.get_embedding_model()
            # Use encode_query for better query optimization
            query_embedding = embedding_model.encode_query(query)
            if query_embedding is None:
                # Fall back to TF-IDF if embeddings failed
                return self._tfidf_keyword_search(query, k)
                
            query_words = self._tokenize(query)
            results = []
            
            # Import numpy only when we actually need it
            import numpy as np
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT id, content, embedding, metadata FROM documents")
                
                for row in cursor.fetchall():
                    doc_id, content, embedding_blob, metadata_str = row
                    
                    # Vector similarity score
                    vector_score = 0.0
                    if embedding_blob:
                        doc_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                        # Cosine similarity
                        similarity = np.dot(query_embedding, doc_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                        )
                        vector_score = max(0, similarity)  # Ensure non-negative
                    
                    # TF-IDF score
                    tfidf_score = self._calculate_tfidf_score(query_words, doc_id, content)
                    
                    # Keyword score
                    keyword_score = self._calculate_keyword_score(query_words, content)
                    
                    # Combined score (weighted: 70% vector, 20% TF-IDF, 10% keyword)
                    # Higher weight on vector similarity since Cohere is very good
                    combined_score = (0.7 * vector_score) + (0.2 * tfidf_score) + (0.1 * keyword_score)
                    
                    if combined_score > 0.1:
                        results.append({
                            "content": content,
                            "score": float(combined_score),
                            "metadata": json.loads(metadata_str) if metadata_str else {},
                            "search_type": "hybrid_cohere"
                        })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:k]
            
        except Exception as e:
            print(f"⚠️ Cohere embedding search failed: {e}")
            return self._tfidf_keyword_search(query, k)

    def _tfidf_keyword_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Fallback TF-IDF + keyword search"""
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
                    "search_type": "hybrid_tfidf"
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
        """Pure vector similarity search using Cohere"""
        try:
            embedding_model = self.get_embedding_model()
            query_embedding = embedding_model.encode_query(query)
            if query_embedding is None:
                # Fall back to TF-IDF if no embeddings available
                return self.search_similar(query, k)
            
            # Import numpy only when we actually need it
            import numpy as np
            results = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT id, content, embedding, metadata FROM documents WHERE embedding IS NOT NULL")
                
                for row in cursor.fetchall():
                    doc_id, content, embedding_blob, metadata_str = row
                    
                    if embedding_blob:
                        doc_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                        
                        # Cosine similarity
                        similarity = np.dot(query_embedding, doc_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                        )
                        
                        if similarity > 0.1:  # Minimum similarity threshold
                            results.append({
                                "content": content,
                                "score": float(similarity),
                                "metadata": json.loads(metadata_str) if metadata_str else {},
                                "search_type": "vector_cohere"
                            })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:k]
            
        except Exception as e:
            print(f"⚠️ Vector search failed: {e}")
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
        embedding_model = self.get_embedding_model()
        return {
            "total_documents": len(self.documents),
            "unique_words": len(self.document_frequencies),
            "database_path": self.db_path,
            "embedding_model": "Cohere embed-english-light-v3.0" if embedding_model.client else "TF-IDF fallback",
            "cohere_api_key_set": bool(embedding_model.api_key)
        }