import json
import re
import math
import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database_config import get_db, Document, create_tables

# Import Cohere embeddings only when needed
def get_cohere_embeddings():
    from cohere_embeddings import CohereEmbeddings
    return CohereEmbeddings()

class PostgresHybridVectorSearch:
    def __init__(self):
        # Initialize Cohere embeddings lazily
        self.embedding_model = None
        
        # Create tables if they don't exist
        create_tables()
        
        # Initialize in-memory caches for TF-IDF
        self.word_frequencies = defaultdict(lambda: defaultdict(int))
        self.document_frequencies = defaultdict(int)
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
                    @property
                    def client(self):
                        return None
                    @property
                    def api_key(self):
                        return None
                self.embedding_model = DummyEmbeddings()
        return self.embedding_model

    def _load_existing_documents(self):
        """Load existing documents from PostgreSQL for TF-IDF calculations"""
        db = next(get_db())
        try:
            documents = db.query(Document).all()
            for doc in documents:
                self._update_frequencies(doc.content, doc.id)
        finally:
            db.close()

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
        """Add a document with embeddings to PostgreSQL"""
        # Generate Cohere embedding
        embedding_blob = None
        try:
            embedding_model = self.get_embedding_model()
            embedding = embedding_model.encode(content)
            if embedding is not None:
                embedding_blob = embedding.tobytes()
        except Exception as e:
            print(f"⚠️ Failed to generate embedding: {e}")
        
        # Save to PostgreSQL
        db = next(get_db())
        try:
            doc = Document(
                content=content,
                embedding=embedding_blob,
                doc_metadata=metadata
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            
            # Update TF-IDF frequencies
            self._update_frequencies(content, doc.id)
            
            print(f"✅ Document added with ID: {doc.id}")
            return doc.id
            
        except Exception as e:
            db.rollback()
            print(f"❌ Failed to add document: {e}")
            raise
        finally:
            db.close()

    def _calculate_tfidf_score(self, query_words: List[str], doc_id: int, content: str) -> float:
        if not query_words:
            return 0.0
        
        score = 0.0
        doc_word_count = sum(self.word_frequencies[doc_id].values())
        total_docs = len(self.word_frequencies)
        
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
            query_embedding = embedding_model.encode_query(query)
            if query_embedding is None:
                return self._tfidf_keyword_search(query, k)
                
            query_words = self._tokenize(query)
            results = []
            
            db = next(get_db())
            try:
                documents = db.query(Document).filter(Document.embedding.isnot(None)).all()
                
                for doc in documents:
                    # Vector similarity score
                    vector_score = 0.0
                    if doc.embedding:
                        doc_embedding = np.frombuffer(doc.embedding, dtype=np.float32)
                        # Cosine similarity
                        similarity = np.dot(query_embedding, doc_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                        )
                        vector_score = max(0, similarity)
                    
                    # TF-IDF score
                    tfidf_score = self._calculate_tfidf_score(query_words, doc.id, doc.content)
                    
                    # Keyword score
                    keyword_score = self._calculate_keyword_score(query_words, doc.content)
                    
                    # Combined score (weighted: 70% vector, 20% TF-IDF, 10% keyword)
                    combined_score = (0.7 * vector_score) + (0.2 * tfidf_score) + (0.1 * keyword_score)
                    
                    if combined_score > 0.1:
                        results.append({
                            "id": doc.id,
                            "content": doc.content,
                            "score": float(combined_score),
                            "metadata": doc.doc_metadata or {},
                            "search_type": "hybrid_cohere",
                            "created_at": doc.created_at.isoformat() if doc.created_at else None
                        })
            finally:
                db.close()
            
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
        db = next(get_db())
        try:
            documents = db.query(Document).all()
            
            for doc in documents:
                # Calculate TF-IDF score
                tfidf_score = self._calculate_tfidf_score(query_words, doc.id, doc.content)
                
                # Calculate keyword match score
                keyword_score = self._calculate_keyword_score(query_words, doc.content)
                
                # Combined score (weighted)
                combined_score = (0.7 * tfidf_score) + (0.3 * keyword_score)
                
                if combined_score > 0:
                    results.append({
                        "id": doc.id,
                        "content": doc.content,
                        "score": combined_score,
                        "metadata": doc.metadata or {},
                        "search_type": "hybrid_tfidf",
                        "created_at": doc.created_at.isoformat() if doc.created_at else None
                    })
        finally:
            db.close()
        
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
        query_words = self._tokenize(query)
        results = []
        
        db = next(get_db())
        try:
            documents = db.query(Document).all()
            
            for doc in documents:
                score = self._calculate_keyword_score(query_words, doc.content)
                if score > 0:
                    results.append({
                        "id": doc.id,
                        "content": doc.content,
                        "score": score,
                        "metadata": doc.metadata or {},
                        "search_type": "keyword",
                        "created_at": doc.created_at.isoformat() if doc.created_at else None
                    })
        finally:
            db.close()
        
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
            
            results = []
            
            db = next(get_db())
            try:
                documents = db.query(Document).filter(Document.embedding.isnot(None)).all()
                
                for doc in documents:
                    if doc.embedding:
                        doc_embedding = np.frombuffer(doc.embedding, dtype=np.float32)
                        
                        # Cosine similarity
                        similarity = np.dot(query_embedding, doc_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                        )
                        
                        if similarity > 0.1:  # Minimum similarity threshold
                            results.append({
                                "id": doc.id,
                                "content": doc.content,
                                "score": float(similarity),
                                "metadata": doc.doc_metadata or {},
                                "search_type": "vector_cohere",
                                "created_at": doc.created_at.isoformat() if doc.created_at else None
                            })
            finally:
                db.close()
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:k]
            
        except Exception as e:
            print(f"⚠️ Vector search failed: {e}")
            return self.search_similar(query, k)

    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        db = next(get_db())
        try:
            total_docs = db.query(Document).count()
            docs_with_embeddings = db.query(Document).filter(Document.embedding.isnot(None)).count()
        finally:
            db.close()
            
        embedding_model = self.get_embedding_model()
        return {
            "total_documents": total_docs,
            "documents_with_embeddings": docs_with_embeddings,
            "unique_words": len(self.document_frequencies),
            "database": "PostgreSQL",
            "embedding_model": "Cohere embed-english-light-v3.0" if embedding_model.client else "TF-IDF fallback",
            "cohere_api_key_set": bool(getattr(embedding_model, 'api_key', None))
        }
