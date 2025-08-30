"""
Add test content to the database for plugin testing
"""

from postgres_hybrid_search import PostgresHybridVectorSearch

def add_test_documents():
    """Add some test documents to the database"""
    search_engine = PostgresHybridVectorSearch()
    
    test_documents = [
        {
            "content": "Machine learning is a subset of artificial intelligence that focuses on the use of data and algorithms to imitate the way humans learn, gradually improving accuracy over time. It includes techniques like neural networks, deep learning, and natural language processing.",
            "metadata": {"category": "AI/ML", "source": "test", "type": "definition"}
        },
        {
            "content": "Python is a high-level programming language widely used for data science, web development, and automation. It's known for its simple syntax and extensive library ecosystem including NumPy, Pandas, and TensorFlow.",
            "metadata": {"category": "Programming", "source": "test", "type": "definition"}
        },
        {
            "content": "PostgreSQL is a powerful, open-source relational database system that supports both SQL and JSON queries. It's excellent for applications requiring complex queries and data integrity.",
            "metadata": {"category": "Database", "source": "test", "type": "definition"}
        },
        {
            "content": "Vector embeddings are numerical representations of data that capture semantic meaning. They allow computers to understand and process text, images, and other data types in a way that preserves relationships and similarities.",
            "metadata": {"category": "AI/ML", "source": "test", "type": "concept"}
        },
        {
            "content": "ChatGPT plugins extend the capabilities of ChatGPT by allowing it to access external APIs and databases. This enables ChatGPT to provide more accurate and up-to-date information by retrieving data from specialized sources.",
            "metadata": {"category": "AI/ML", "source": "test", "type": "concept"}
        }
    ]
    
    print("📝 Adding test documents to database...")
    
    for i, doc in enumerate(test_documents, 1):
        try:
            doc_id = search_engine.add_document(doc["content"], doc["metadata"])
            print(f"✅ Added document {i}: {doc['content'][:50]}... (ID: {doc_id})")
        except Exception as e:
            print(f"❌ Failed to add document {i}: {e}")
    
    # Get updated stats
    stats = search_engine.get_stats()
    print(f"\n📊 Database now has {stats['total_documents']} total documents")
    print(f"   Documents with embeddings: {stats['documents_with_embeddings']}")

if __name__ == "__main__":
    add_test_documents()
