import os
from typing import Optional, List

class CohereEmbeddings:
    def __init__(self):
        self.api_key = os.getenv('COHERE_API_KEY')
        self.client = None
        self.embedding_size = 1024  # Cohere embed-english-light-v3.0 dimension
        
        if self.api_key:
            try:
                import cohere
                self.client = cohere.Client(self.api_key)
                print("✅ Cohere client initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize Cohere: {e}")
                self.client = None
        else:
            print("⚠️ COHERE_API_KEY not set - vector search will use TF-IDF fallback")
    
    def encode(self, text: str):
        """Generate embeddings using Cohere API"""
        if not self.client:
            return None
        
        try:
            # Use the lightweight model for speed and efficiency
            response = self.client.embed(
                texts=[text],
                model='embed-english-light-v3.0',
                input_type='search_document'
            )
            
            # Convert to numpy array
            import numpy as np
            embedding = np.array(response.embeddings[0], dtype=np.float32)
            return embedding
            
        except Exception as e:
            print(f"⚠️ Cohere embedding failed: {e}")
            return None
    
    def encode_batch(self, texts: List[str]):
        """Generate embeddings for multiple texts at once (more efficient)"""
        if not self.client:
            return None
        
        try:
            response = self.client.embed(
                texts=texts,
                model='embed-english-light-v3.0',
                input_type='search_document'
            )
            
            import numpy as np
            embeddings = [np.array(emb, dtype=np.float32) for emb in response.embeddings]
            return embeddings
            
        except Exception as e:
            print(f"⚠️ Cohere batch embedding failed: {e}")
            return None
    
    def encode_query(self, query: str):
        """Generate embeddings for search queries"""
        if not self.client:
            return None
        
        try:
            response = self.client.embed(
                texts=[query],
                model='embed-english-light-v3.0',
                input_type='search_query'  # Optimized for queries
            )
            
            import numpy as np
            embedding = np.array(response.embeddings[0], dtype=np.float32)
            return embedding
            
        except Exception as e:
            print(f"⚠️ Cohere query embedding failed: {e}")
            return None
