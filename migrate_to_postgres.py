import sqlite3
import json
from database_config import get_db, Document, create_tables

def migrate_from_sqlite():
    """Migrate existing SQLite data to PostgreSQL"""
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Create PostgreSQL tables
    create_tables()
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect("search_data.db")
        sqlite_cursor = sqlite_conn.execute("SELECT content, embedding, metadata FROM documents")
        
        # Get PostgreSQL session
        db = next(get_db())
        
        try:
            migrated_count = 0
            for row in sqlite_cursor.fetchall():
                content, embedding_blob, metadata_str = row
                
                # Parse metadata
                metadata = None
                if metadata_str:
                    try:
                        metadata = json.loads(metadata_str)
                    except:
                        metadata = {"original_metadata": metadata_str}
                
                # Create new document in PostgreSQL
                doc = Document(
                    content=content,
                    embedding=embedding_blob,
                    doc_metadata=metadata
                )
                db.add(doc)
                migrated_count += 1
                
                if migrated_count % 100 == 0:
                    print(f"✅ Migrated {migrated_count} documents...")
            
            db.commit()
            print(f"🎉 Successfully migrated {migrated_count} documents to PostgreSQL!")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Migration failed: {e}")
            raise
        finally:
            db.close()
            sqlite_conn.close()
            
    except FileNotFoundError:
        print("ℹ️ No existing SQLite database found. Starting fresh with PostgreSQL.")
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_from_sqlite()
