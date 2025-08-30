#!/usr/bin/env python3
"""
Migrate existing quilt-test data from SQLite to PostgreSQL
"""

import sqlite3
import psycopg2
import json
from datetime import datetime
import cohere
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_sqlite_to_postgres():
    """Migrate data from old SQLite to new PostgreSQL system"""
    
    # PostgreSQL config
    pg_config = {
        "host": "localhost",
        "port": "5432",
        "database": "quilt_embeddings",
        "user": "quilt_user",
        "password": "your_secure_password"
    }
    
    # Cohere setup
    cohere_api_key = os.getenv('COHERE_API_KEY')
    cohere_client = cohere.Client(cohere_api_key) if cohere_api_key else None
    
    print("🔄 MIGRATING QUILT-TEST DATA TO POSTGRESQL")
    print("=" * 50)
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect('search_data.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get all documents from SQLite
        sqlite_cursor.execute("SELECT content, metadata FROM documents")
        sqlite_docs = sqlite_cursor.fetchall()
        
        print(f"📥 Found {len(sqlite_docs)} documents in SQLite")
        
        if len(sqlite_docs) == 0:
            print("❌ No documents to migrate")
            return
        
        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(**pg_config)
        pg_cursor = pg_conn.cursor()
        
        migrated_count = 0
        
        for content, metadata_str in sqlite_docs:
            try:
                # Parse metadata
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Create enhanced metadata for PostgreSQL
                enhanced_metadata = {
                    'source': 'migrated_quilt_test',
                    'original_source': 'sqlite_search_data',
                    'repo_name': 'quilt-test',
                    'user_id': 'web_app_user',
                    'file_path': metadata.get('source_file', 'unknown'),
                    'title': metadata.get('title', ''),
                    'migrated_at': datetime.now().isoformat(),
                    'original_metadata': metadata
                }
                
                # Generate embedding if Cohere is available
                embedding_binary = None
                if cohere_client and content.strip():
                    try:
                        response = cohere_client.embed(
                            texts=[content],
                            model='embed-english-v3.0',
                            input_type='search_document'
                        )
                        import numpy as np
                        embedding_array = np.array(response.embeddings[0], dtype=np.float32)
                        embedding_binary = embedding_array.tobytes()
                        print(f"✅ Generated embedding for: {metadata.get('title', 'content')}")
                    except Exception as e:
                        print(f"⚠️  Embedding error for {metadata.get('title', 'content')}: {e}")
                
                # Insert into PostgreSQL
                pg_cursor.execute(
                    """INSERT INTO documents (content, embedding, doc_metadata, created_at) 
                       VALUES (%s, %s, %s, %s)""",
                    (content, embedding_binary, json.dumps(enhanced_metadata), datetime.now())
                )
                
                migrated_count += 1
                print(f"📄 Migrated: {metadata.get('title', 'Untitled content')}")
                
            except Exception as e:
                print(f"❌ Error migrating document: {e}")
                continue
        
        # Commit PostgreSQL changes
        pg_conn.commit()
        
        # Close connections
        sqlite_conn.close()
        pg_conn.close()
        
        print(f"\n🎉 Migration Complete!")
        print(f"📊 Successfully migrated: {migrated_count} documents")
        print(f"🔍 Claude Desktop can now search your quilt-test content!")
        
        return migrated_count
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return 0

if __name__ == "__main__":
    migrate_sqlite_to_postgres()
