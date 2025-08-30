#!/usr/bin/env python3
"""
Database Viewer - Explore your PostgreSQL and SQLite databases
"""

import psycopg2
import sqlite3
import json
from datetime import datetime

class DatabaseViewer:
    def __init__(self):
        self.pg_config = {
            "host": "localhost",
            "port": "5432",
            "database": "quilt_embeddings",
            "user": "quilt_user",
            "password": "your_secure_password"
        }
        self.sqlite_db = "quilt_deployments.db"

    def view_postgresql(self):
        """View PostgreSQL database contents"""
        print("🗄️  POSTGRESQL DATABASE (Main Search Database)")
        print("=" * 60)
        
        try:
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor()
            
            # Total documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            total = cursor.fetchone()[0]
            print(f"📊 Total Documents: {total}")
            
            # By source
            print(f"\n📁 Documents by Source:")
            cursor.execute("""
                SELECT doc_metadata->>'source' as source, COUNT(*) as count
                FROM documents 
                GROUP BY doc_metadata->>'source'
                ORDER BY count DESC
            """)
            
            for source, count in cursor.fetchall():
                source_name = source if source else "Unknown"
                print(f"   {source_name}: {count} documents")
            
            # Recent documents
            print(f"\n📄 Recent Documents (last 10):")
            cursor.execute("""
                SELECT 
                    doc_metadata->>'file_path' as file_path,
                    doc_metadata->>'repo_name' as repo_name,
                    LENGTH(content) as content_length,
                    created_at
                FROM documents 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            
            for i, (file_path, repo_name, length, created_at) in enumerate(cursor.fetchall(), 1):
                file_name = file_path if file_path else "Unknown file"
                repo = repo_name if repo_name else "Unknown repo"
                print(f"   {i:2d}. {file_name} ({length} chars) - {repo}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error connecting to PostgreSQL: {e}")

    def view_sqlite(self):
        """View SQLite database contents"""
        print(f"\n🗃️  SQLITE DATABASE (Deployment Tracking)")
        print("=" * 60)
        
        try:
            if not os.path.exists(self.sqlite_db):
                print("❌ SQLite database not found")
                return
                
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            
            # Total deployments
            cursor.execute("SELECT COUNT(*) FROM deployments")
            total_deployments = cursor.fetchone()[0]
            print(f"📊 Total Deployments: {total_deployments}")
            
            if total_deployments > 0:
                # Deployments by user
                print(f"\n👥 Deployments by User:")
                cursor.execute("""
                    SELECT user_id, COUNT(*) as count, SUM(pg_documents_added) as total_docs
                    FROM deployments 
                    GROUP BY user_id
                    ORDER BY count DESC
                """)
                
                for user_id, count, total_docs in cursor.fetchall():
                    docs = total_docs if total_docs else 0
                    print(f"   {user_id}: {count} deployments, {docs} documents indexed")
                
                # Recent deployments
                print(f"\n🚀 Recent Deployments:")
                cursor.execute("""
                    SELECT repo_name, user_id, deployed_at, pg_documents_added
                    FROM deployments 
                    ORDER BY deployed_at DESC 
                    LIMIT 10
                """)
                
                for i, (repo_name, user_id, deployed_at, docs_added) in enumerate(cursor.fetchall(), 1):
                    docs = docs_added if docs_added else 0
                    print(f"   {i:2d}. {repo_name} by {user_id} - {docs} docs indexed")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error connecting to SQLite: {e}")

    def search_content(self, query):
        """Search content in PostgreSQL"""
        print(f"\n🔍 SEARCH RESULTS for: '{query}'")
        print("=" * 60)
        
        try:
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor()
            
            # Simple search
            search_query = f"%{query.lower()}%"
            cursor.execute("""
                SELECT 
                    doc_metadata->>'file_path' as file_path,
                    doc_metadata->>'repo_name' as repo_name,
                    LEFT(content, 200) as content_preview
                FROM documents 
                WHERE LOWER(content) LIKE %s
                ORDER BY created_at DESC
                LIMIT 5
            """, (search_query,))
            
            results = cursor.fetchall()
            if results:
                for i, (file_path, repo_name, preview) in enumerate(results, 1):
                    file_name = file_path if file_path else "Unknown"
                    repo = repo_name if repo_name else "Unknown"
                    print(f"\n{i}. {file_name} - {repo}")
                    print(f"   Preview: {preview}...")
            else:
                print("   No results found")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Search error: {e}")

def main():
    import os
    
    viewer = DatabaseViewer()
    
    print("🔍 QUILT DATABASE VIEWER")
    print("=" * 40)
    
    # View PostgreSQL
    viewer.view_postgresql()
    
    # View SQLite
    viewer.view_sqlite()
    
    # Interactive search
    print(f"\n🔍 SEARCH YOUR CONTENT:")
    print("Enter search terms to find content (or 'quit' to exit)")
    
    while True:
        query = input("\nSearch: ").strip()
        if query.lower() in ['quit', 'exit', '']:
            break
        viewer.search_content(query)
    
    print("\n👋 Database viewer closed")

if __name__ == "__main__":
    import os
    main()
