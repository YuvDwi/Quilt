import sqlite3
import json
import re
import math
import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

class HybridVectorSearch:
    def __init__(self):
        self.db_path = "search_data.db"
        self.documents = []
        self.word_frequencies = defaultdict(lambda: defaultdict(int))
        self.document_frequencies = defaultdict(int)
        
        # Initialize lightweight sentence transformer
        self.model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L3-v2')  # Only 61MB
                print("✅ Loaded lightweight embedding model (61MB)")
            except Exception as e:
                print(f"⚠️ Failed to load embedding model: {e}")
                self.model = None
        
        self.init_database()
        self._load_existing_documents()

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
        # Generate embedding if model is available
        embedding_blob = None
        if self.model:
            try:
                embedding = self.model.encode(content)
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
        """Hybrid search combining embeddings, TF-IDF and keyword matching"""
        if not self.documents:
            return []
        
        # If we have embeddings, use vector + TF-IDF hybrid
        if self.model:
            return self._hybrid_embedding_search(query, k)
        
        # Fall back to TF-IDF + keyword hybrid
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
    
    def _hybrid_embedding_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Advanced hybrid search using embeddings + TF-IDF + keywords"""
        try:
            query_embedding = self.model.encode(query)
            query_words = self._tokenize(query)
            results = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT id, content, embedding, metadata FROM documents")
                
                for row in cursor.fetchall():
                    doc_id, content, embedding_blob, metadata_str = row
                    
                    # Vector similarity score
                    vector_score = 0.0
                    if embedding_blob:
                        doc_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                        vector_score = np.dot(query_embedding, doc_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                        )
                    
                    # TF-IDF score
                    tfidf_score = self._calculate_tfidf_score(query_words, doc_id, content)
                    
                    # Keyword score
                    keyword_score = self._calculate_keyword_score(query_words, content)
                    
                    # Combined score (weighted: 50% vector, 30% TF-IDF, 20% keyword)
                    combined_score = (0.5 * vector_score) + (0.3 * tfidf_score) + (0.2 * keyword_score)
                    
                    if combined_score > 0.1:
                        results.append({
                            "content": content,
                            "score": float(combined_score),
                            "metadata": json.loads(metadata_str) if metadata_str else {},
                            "search_type": "hybrid_embedding"
                        })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:k]
            
        except Exception as e:
            print(f"⚠️ Hybrid embedding search failed: {e}")
            # Fall back to TF-IDF search
            return self.search_similar(query, k)

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
        """Vector similarity search using lightweight embeddings"""
        if not self.model:
            # Fall back to TF-IDF if no embeddings available
            return self.search_similar(query, k)
        
        try:
            query_embedding = self.model.encode(query)
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
                                "search_type": "vector_embedding"
                            })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:k]
            
        except Exception as e:
            print(f"⚠️ Vector search failed: {e}")
            return self.search_similar(query, k)  # Fall back to TF-IDF

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