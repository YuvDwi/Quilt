"""
Debug the search functionality
"""

from postgres_hybrid_search import PostgresHybridVectorSearch

def test_search_directly():
    """Test search functionality directly"""
    try:
        print("🔍 Testing search engine directly...")
        search_engine = PostgresHybridVectorSearch()
        
        # Test keyword search
        print("\n1. Testing keyword search:")
        results = search_engine.keyword_search("machine learning", k=3)
        print(f"   Found {len(results)} results")
        for i, result in enumerate(results[:2], 1):
            print(f"   {i}. Score: {result['score']:.3f} - {result['content'][:100]}...")
        
        # Test hybrid search
        print("\n2. Testing hybrid search:")
        results = search_engine.search_similar("python programming", k=3)
        print(f"   Found {len(results)} results")
        for i, result in enumerate(results[:2], 1):
            print(f"   {i}. Score: {result['score']:.3f} - {result['content'][:100]}...")
        
        # Test vector search
        print("\n3. Testing vector search:")
        results = search_engine.vector_search("database", k=3)
        print(f"   Found {len(results)} results")
        for i, result in enumerate(results[:2], 1):
            print(f"   {i}. Score: {result['score']:.3f} - {result['content'][:100]}...")
            
        print("\n✅ Direct search testing completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Direct search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_search_directly()
