"""
Test PostgreSQL setup for Quilt Embeddings
"""

import os
from postgres_hybrid_search import PostgresHybridVectorSearch

def test_database_connection():
    """Test basic database connection and operations"""
    print("🔍 Testing PostgreSQL setup...")
    
    try:
        # Initialize search engine (this will create tables)
        search_engine = PostgresHybridVectorSearch()
        print("✅ Successfully connected to PostgreSQL")
        
        # Test adding a document
        doc_id = search_engine.add_document(
            "This is a test document for PostgreSQL setup verification.",
            metadata={"test": True, "setup": "postgres"}
        )
        print(f"✅ Successfully added test document with ID: {doc_id}")
        
        # Test searching
        results = search_engine.search_similar("test document", k=1)
        if results:
            print(f"✅ Search working - found {len(results)} result(s)")
            print(f"   First result score: {results[0]['score']:.3f}")
        else:
            print("⚠️ Search returned no results")
        
        # Get stats
        stats = search_engine.get_stats()
        print("✅ Database statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n🎉 PostgreSQL setup is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL setup test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your .env file has correct database credentials")
        print("3. Verify the database and user were created correctly")
        print("4. Run: python setup_postgres.py")
        return False

def test_environment_variables():
    """Test that required environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = {
        'DATABASE_URL': 'Database connection string',
        'COHERE_API_KEY': 'Cohere API key (optional but recommended)'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
            print(f"⚠️ Missing: {var}")
        else:
            print(f"✅ Found: {var}")
    
    if missing_vars:
        print(f"\nPlease set these environment variables in your .env file:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 PostgreSQL Setup Test")
    print("=" * 40)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test database connection
    db_ok = test_database_connection()
    
    print("\n" + "=" * 40)
    if env_ok and db_ok:
        print("🎉 All tests passed! PostgreSQL setup is complete.")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    return env_ok and db_ok

if __name__ == "__main__":
    main()
