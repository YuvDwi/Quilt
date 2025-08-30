#!/usr/bin/env python3
"""
Integrated Quilt Deployer with PostgreSQL Indexing
This replaces the existing deployment system to automatically index content
into PostgreSQL for Claude Desktop search
"""

import os
import sqlite3
import json
import requests
import zipfile
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any, List
import psycopg2
import cohere
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import hashlib
import base64

# Load environment variables
load_dotenv()

class IntegratedQuiltDeployer:
    def __init__(self):
        self.db_path = "quilt_deployments.db"
        
        # PostgreSQL configuration
        self.pg_config = {
            "host": "localhost",
            "port": "5432",
            "database": "quilt_embeddings",
            "user": "quilt_user",
            "password": "your_secure_password"
        }
        
        # Cohere for embeddings
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        if self.cohere_api_key:
            self.cohere_client = cohere.Client(self.cohere_api_key)
        else:
            self.cohere_client = None
            print("⚠️  No Cohere API key found - will index without embeddings")
        
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for deployment tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    repo_name TEXT NOT NULL,
                    repo_url TEXT NOT NULL,
                    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'deployed',
                    sections_indexed INTEGER DEFAULT 0,
                    pg_documents_added INTEGER DEFAULT 0
                )
            """)

    def generate_embedding(self, text: str):
        """Generate Cohere embedding for text"""
        if not self.cohere_client or not text.strip():
            return None
        
        try:
            response = self.cohere_client.embed(
                texts=[text],
                model='embed-english-v3.0',
                input_type='search_document'  # Required parameter
            )
            return response.embeddings[0]
        except Exception as e:
            print(f"⚠️  Embedding error: {e}")
            return None

    def extract_content_from_file(self, file_path: str, content: str) -> str:
        """Extract readable text from file content"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.html', '.htm']:
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        elif file_ext == '.md':
            # For markdown, use as-is
            return content
            
        elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
            # Extract comments and meaningful content from code
            lines = content.split('\n')
            extracted = []
            
            for line in lines:
                # Extract comments
                if '//' in line:
                    comment = line.split('//')[1].strip()
                    if len(comment) > 10:  # Meaningful comments
                        extracted.append(comment)
                
                # Extract JSDoc comments
                if '/**' in line or '*' in line.strip():
                    cleaned = line.strip().replace('*', '').strip()
                    if len(cleaned) > 10:
                        extracted.append(cleaned)
            
            # If we have extracted content, use it, otherwise use first part of file
            return ' '.join(extracted) if extracted else content[:1000]
            
        elif file_ext in ['.txt', '.py', '.css']:
            return content[:2000]  # First 2000 chars
            
        else:
            # Skip binary or unknown files
            return ""

    def save_to_postgresql(self, content: str, metadata: dict) -> bool:
        """Save content to PostgreSQL database for Claude Desktop search"""
        try:
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor()
            
            # Check if this content already exists (avoid duplicates)
            content_hash = hashlib.md5(content.encode()).hexdigest()
            cursor.execute(
                "SELECT id FROM documents WHERE doc_metadata->>'content_hash' = %s",
                (content_hash,)
            )
            
            if cursor.fetchone():
                print(f"📋 Already indexed: {metadata.get('file_path', 'unknown')}")
                conn.close()
                return False
            
            # Generate embedding
            embedding_binary = None
            if self.cohere_client and content.strip():
                embedding = self.generate_embedding(content)
                if embedding:
                    import numpy as np
                    embedding_array = np.array(embedding, dtype=np.float32)
                    embedding_binary = embedding_array.tobytes()
            
            # Add content hash to metadata
            metadata['content_hash'] = content_hash
            metadata['indexed_via'] = 'quilt_deployment'
            metadata['indexed_at'] = datetime.now().isoformat()
            
            # Insert into PostgreSQL
            cursor.execute(
                """INSERT INTO documents (content, embedding, doc_metadata, created_at) 
                   VALUES (%s, %s, %s, %s)""",
                (content, embedding_binary, json.dumps(metadata), datetime.now())
            )
            
            conn.commit()
            conn.close()
            
            print(f"✅ Indexed to PostgreSQL: {metadata.get('file_path', 'content')} ({len(content)} chars)")
            return True
            
        except Exception as e:
            print(f"❌ PostgreSQL error for {metadata.get('file_path', 'content')}: {e}")
            return False

    def process_repository_files(self, repo_path: str, repo_name: str, repo_url: str, user_id: str) -> int:
        """Process repository files and index them into PostgreSQL"""
        indexed_count = 0
        content_extensions = {'.html', '.htm', '.md', '.txt', '.js', '.jsx', '.ts', '.tsx', '.py', '.css'}
        
        for root, dirs, files in os.walk(repo_path):
            # Skip node_modules, .git, dist, build directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'dist', 'build', '.next', '__pycache__']]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in content_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Extract meaningful text
                        text_content = self.extract_content_from_file(relative_path, content)
                        
                        # Skip if content is too short
                        if len(text_content.strip()) < 50:
                            continue
                        
                        # Prepare metadata
                        metadata = {
                            'file_path': relative_path,
                            'repo_name': repo_name,
                            'repo_url': repo_url,
                            'user_id': user_id,
                            'file_type': file_ext,
                            'source': 'quilt_deployment'
                        }
                        
                        # Save to PostgreSQL
                        if self.save_to_postgresql(text_content, metadata):
                            indexed_count += 1
                        
                        # Limit to prevent overwhelming
                        if indexed_count >= 50:
                            print(f"⚠️  Reached indexing limit (50 files)")
                            break
                            
                    except Exception as e:
                        print(f"❌ Error processing {relative_path}: {e}")
                        continue
            
            if indexed_count >= 50:
                break
        
        return indexed_count

    def deploy_repository(self, user_id: str, repo_url: str, access_token: str) -> Dict[str, Any]:
        """Deploy repository and index content into PostgreSQL"""
        try:
            print(f"🚀 Starting deployment: {repo_url}")
            
            # Extract owner/repo from URL
            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) < 2:
                raise Exception("Invalid repository URL")
            
            owner, repo = parts[0], parts[1]
            repo_name = f"{owner}/{repo}"
            
            # Download repository as ZIP
            headers = {'Authorization': f'token {access_token}'} if access_token else {}
            zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/main"
            
            print(f"📥 Downloading repository: {repo_name}")
            response = requests.get(zip_url, headers=headers)
            response.raise_for_status()
            
            # Extract to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, f"{repo}.zip")
                
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                # Extract ZIP
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find the extracted directory (GitHub adds a hash to the folder name)
                extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                if not extracted_dirs:
                    raise Exception("Failed to extract repository")
                
                repo_path = os.path.join(temp_dir, extracted_dirs[0])
                
                # Process files and index into PostgreSQL
                print(f"📄 Processing files from {repo_name}")
                pg_documents_added = self.process_repository_files(repo_path, repo_name, repo_url, user_id)
            
            # Record deployment in SQLite (for web app tracking)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO deployments 
                       (user_id, repo_name, repo_url, sections_indexed, pg_documents_added) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, repo_name, repo_url, pg_documents_added, pg_documents_added)
                )
            
            print(f"🎉 Deployment complete: {repo_name}")
            print(f"📊 Added {pg_documents_added} documents to PostgreSQL")
            print(f"🔍 Claude Desktop can now search this content!")
            
            return {
                'status': 'success',
                'repository': repo_name,
                'sections_indexed': pg_documents_added,
                'postgres_documents': pg_documents_added,
                'message': f'Successfully deployed and indexed {pg_documents_added} files'
            }
            
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'repository': repo_url
            }

    def get_deployments(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's deployments"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT repo_name, repo_url, deployed_at, sections_indexed, pg_documents_added 
                   FROM deployments WHERE user_id = ? ORDER BY deployed_at DESC""",
                (user_id,)
            )
            deployments = [
                {
                    'repo_name': row[0],
                    'repo_url': row[1], 
                    'deployed_at': row[2],
                    'sections_indexed': row[3],
                    'postgres_documents': row[4] if row[4] else row[3]
                }
                for row in cursor.fetchall()
            ]
        
        return deployments

# Example usage
if __name__ == "__main__":
    deployer = IntegratedQuiltDeployer()
    
    # Test deployment
    test_repo = "https://github.com/microsoft/vscode-docs"
    result = deployer.deploy_repository("test_user", test_repo, "")
    print(f"\nResult: {result}")
