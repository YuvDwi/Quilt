"""
Test the search functionality directly
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_search():
    """Test direct search without FastAPI"""
    try:
        # Connect to database
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://quilt_user:your_secure_password@localhost:5432/quilt_embeddings"
        )
        
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="quilt_embeddings",
            user="quilt_user",
            password="your_secure_password"
        )
        
        cursor = conn.cursor()
        
        # Test query
        query = "machine learning"
        print(f"🔍 Testing search for: '{query}'")
        
        # Simple search
        cursor.execute("""
            SELECT id, content, doc_metadata
            FROM documents 
            WHERE LOWER(content) LIKE %s
            LIMIT 5
        """, (f"%{query.lower()}%",))
        
        results = cursor.fetchall()
        
        print(f"✅ Found {len(results)} results:")
        for i, (doc_id, content, metadata) in enumerate(results, 1):
            print(f"{i}. ID: {doc_id}")
            print(f"   Content: {content[:100]}...")
            print(f"   Metadata: {metadata}")
            print()
        
        # Test sentence search
        sentence = "What is machine learning"
        words = sentence.lower().split()
        print(f"🔍 Testing sentence search: '{sentence}'")
        
        conditions = []
        params = []
        for word in words:
            if len(word) > 2:
                conditions.append("LOWER(content) LIKE %s")
                params.append(f"%{word}%")
        
        if conditions:
            where_clause = " OR ".join(conditions)
            sql = f"SELECT id, content FROM documents WHERE {where_clause} LIMIT 3"
            
            cursor.execute(sql, params)
            sentence_results = cursor.fetchall()
            
            print(f"✅ Sentence search found {len(sentence_results)} results:")
            for i, (doc_id, content) in enumerate(sentence_results, 1):
                print(f"{i}. ID: {doc_id} - {content[:100]}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_search()
