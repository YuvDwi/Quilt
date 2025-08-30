#!/usr/bin/env python3
"""
Migrate existing local PostgreSQL data to Render cloud database
"""

import os
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv()

def migrate_to_cloud():
    """Migrate data from local PostgreSQL to cloud PostgreSQL"""
    
    # Local PostgreSQL config
    local_config = {
        "host": "localhost",
        "port": "5432", 
        "database": "quilt_embeddings",
        "user": "quilt_user",
        "password": "your_secure_password"
    }
    
    # Cloud PostgreSQL config (from Render)
    cloud_database_url = input("Enter your Render PostgreSQL DATABASE_URL: ")
    
    if not cloud_database_url:
        print("❌ DATABASE_URL required")
        return
    
    print("🔄 MIGRATING LOCAL DATA TO RENDER CLOUD")
    print("=" * 50)
    
    try:
        # Connect to local database
        print("📥 Connecting to local PostgreSQL...")
        local_conn = psycopg2.connect(**local_config)
        local_cursor = local_conn.cursor()
        
        # Get all documents from local
        local_cursor.execute("SELECT content, embedding, doc_metadata, created_at FROM documents")
        local_docs = local_cursor.fetchall()
        
        print(f"📊 Found {len(local_docs)} documents in local database")
        
        if len(local_docs) == 0:
            print("❌ No documents to migrate")
            return
        
        # Connect to cloud database
        print("☁️  Connecting to Render PostgreSQL...")
        cloud_conn = psycopg2.connect(cloud_database_url)
        cloud_cursor = cloud_conn.cursor()
        
        # Create tables in cloud database
        print("🏗️  Creating tables in cloud database...")
        cloud_cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding BYTEA,
                doc_metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        cloud_cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                repo_url TEXT NOT NULL,
                deployed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                status TEXT DEFAULT 'deployed',
                sections_indexed INTEGER DEFAULT 0,
                pg_documents_added INTEGER DEFAULT 0
            )
        """)
        
        # Migrate documents
        migrated_count = 0
        
        for content, embedding, metadata_json, created_at in local_docs:
            try:
                # Parse and enhance metadata
                metadata = json.loads(metadata_json) if metadata_json else {}
                metadata['migrated_from'] = 'local_postgres'
                metadata['migration_date'] = '2024-01-01'
                
                # Insert into cloud database
                cloud_cursor.execute(
                    """INSERT INTO documents (content, embedding, doc_metadata, created_at) 
                       VALUES (%s, %s, %s, %s)""",
                    (content, embedding, json.dumps(metadata), created_at)
                )
                
                migrated_count += 1
                
                if migrated_count % 10 == 0:
                    print(f"📄 Migrated {migrated_count}/{len(local_docs)} documents...")
                
            except Exception as e:
                print(f"⚠️  Error migrating document: {e}")
                continue
        
        # Commit cloud changes
        cloud_conn.commit()
        
        # Close connections
        local_conn.close()
        cloud_conn.close()
        
        print(f"\n🎉 Migration Complete!")
        print(f"📊 Successfully migrated: {migrated_count}/{len(local_docs)} documents")
        print(f"☁️  Your data is now in Render PostgreSQL!")
        print(f"🔍 Claude Desktop can search your cloud database!")
        
        return migrated_count
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return 0

if __name__ == "__main__":
    migrate_to_cloud()
