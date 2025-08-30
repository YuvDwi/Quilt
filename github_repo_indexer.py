#!/usr/bin/env python3
"""
GitHub Repository Content Indexer
Automatically indexes content from GitHub repos that users deploy through Quilt
"""

import requests
import psycopg2
import json
import base64
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import os
from urllib.parse import urlparse
import cohere
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GitHubRepoIndexer:
    def __init__(self, github_token=None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        
        self.db_config = {
            "host": "localhost",
            "port": "5432", 
            "database": "quilt_embeddings",
            "user": "quilt_user",
            "password": "your_secure_password"
        }
        
        # Initialize Cohere client
        if self.cohere_api_key:
            self.cohere_client = cohere.Client(self.cohere_api_key)
        else:
            self.cohere_client = None
            print("⚠️  No Cohere API key found - will index without embeddings")
        
        self.session = requests.Session()
        if self.github_token:
            self.session.headers.update({
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            })

    def get_repo_files(self, repo_url, branch='main'):
        """Get all files from a GitHub repository"""
        try:
            # Parse GitHub URL to get owner/repo
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                raise ValueError("Invalid GitHub repo URL")
            
            owner, repo = path_parts[0], path_parts[1]
            
            print(f"📁 Fetching files from {owner}/{repo} (branch: {branch})")
            
            # Get repository tree
            api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            response = self.session.get(api_url)
            response.raise_for_status()
            
            tree_data = response.json()
            files = []
            
            # Filter for content files
            content_extensions = {'.html', '.htm', '.md', '.txt', '.jsx', '.tsx', '.js', '.ts', '.py', '.css'}
            
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob':  # It's a file
                    file_path = item['path']
                    file_ext = os.path.splitext(file_path)[1].lower()
                    
                    if file_ext in content_extensions:
                        files.append({
                            'path': file_path,
                            'url': item['url'],
                            'sha': item['sha'],
                            'size': item.get('size', 0)
                        })
            
            print(f"📄 Found {len(files)} content files")
            return files, owner, repo
            
        except Exception as e:
            print(f"❌ Error fetching repo files: {e}")
            return [], None, None

    def get_file_content(self, file_url):
        """Get content of a specific file from GitHub"""
        try:
            response = self.session.get(file_url)
            response.raise_for_status()
            
            file_data = response.json()
            
            # Decode base64 content
            content = base64.b64decode(file_data['content']).decode('utf-8')
            return content
            
        except Exception as e:
            print(f"❌ Error fetching file content: {e}")
            return None

    def extract_text_content(self, content, file_path):
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
            # For markdown, we can use it as-is (or parse it)
            return content
            
        elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
            # Extract comments and strings from code
            # Simple extraction - could be improved
            lines = content.split('\n')
            extracted = []
            
            for line in lines:
                # Extract comments
                if '//' in line:
                    comment = line.split('//')[1].strip()
                    if len(comment) > 10:  # Meaningful comments
                        extracted.append(comment)
                
                # Extract JSDoc comments, strings, etc.
                # This is a simple version - could be much more sophisticated
            
            return ' '.join(extracted) if extracted else content[:500]  # Fallback to first 500 chars
            
        else:
            # For other files, return raw content (truncated)
            return content[:1000]

    def generate_embedding(self, text):
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

    def save_to_database(self, file_data, repo_owner, repo_name):
        """Save file content to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check if this exact content already exists
            content_hash = hashlib.md5(file_data['content'].encode()).hexdigest()
            cursor.execute(
                "SELECT id FROM documents WHERE doc_metadata->>'content_hash' = %s",
                (content_hash,)
            )
            
            if cursor.fetchone():
                print(f"📋 Already indexed: {file_data['path']}")
                conn.close()
                return False
            
            # Generate embedding
            embedding_binary = None
            if file_data['text_content']:
                embedding = self.generate_embedding(file_data['text_content'])
                if embedding:
                    # Convert to binary for storage
                    import numpy as np
                    embedding_array = np.array(embedding, dtype=np.float32)
                    embedding_binary = embedding_array.tobytes()
            
            # Prepare metadata
            metadata = {
                'file_path': file_data['path'],
                'repo_owner': repo_owner,
                'repo_name': repo_name,
                'repo_url': f"https://github.com/{repo_owner}/{repo_name}",
                'file_sha': file_data['sha'],
                'file_size': file_data['size'],
                'content_hash': content_hash,
                'source': 'github_repo',
                'indexed_at': datetime.now().isoformat()
            }
            
            # Insert into database
            cursor.execute(
                """INSERT INTO documents (content, embedding, doc_metadata, created_at) 
                   VALUES (%s, %s, %s, %s)""",
                (
                    file_data['text_content'],
                    embedding_binary,
                    json.dumps(metadata),
                    datetime.now()
                )
            )
            
            conn.commit()
            conn.close()
            
            print(f"✅ Indexed: {file_data['path']} ({len(file_data['text_content'])} chars)")
            return True
            
        except Exception as e:
            print(f"❌ Database error for {file_data['path']}: {e}")
            return False

    def index_repository(self, repo_url, branch='main', max_files=50):
        """Index an entire GitHub repository"""
        print(f"🚀 Starting indexing of: {repo_url}")
        
        # Get all files from repo
        files, owner, repo = self.get_repo_files(repo_url, branch)
        if not files:
            print("❌ No files found or error accessing repository")
            return
        
        # Limit number of files to avoid overwhelming the system
        if len(files) > max_files:
            print(f"⚠️  Repository has {len(files)} files, limiting to {max_files}")
            files = files[:max_files]
        
        indexed_count = 0
        
        for file_info in files:
            try:
                # Get file content
                content = self.get_file_content(file_info['url'])
                if not content:
                    continue
                
                # Extract readable text
                text_content = self.extract_text_content(content, file_info['path'])
                if not text_content or len(text_content.strip()) < 50:
                    continue  # Skip files with minimal content
                
                # Prepare file data
                file_data = {
                    'path': file_info['path'],
                    'content': content,
                    'text_content': text_content,
                    'sha': file_info['sha'],
                    'size': file_info['size']
                }
                
                # Save to database
                if self.save_to_database(file_data, owner, repo):
                    indexed_count += 1
                
                # Small delay to be respectful to GitHub API
                import time
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error processing {file_info['path']}: {e}")
                continue
        
        print(f"🎉 Indexing complete!")
        print(f"📊 Successfully indexed: {indexed_count} files")
        return indexed_count

def main():
    print("🐙 GITHUB REPOSITORY INDEXER")
    print("=" * 50)
    print("Index content from GitHub repositories for Claude Desktop search")
    print()
    
    # Example repositories - replace with actual user repos
    repositories = [
        "https://github.com/vercel/next.js",  # Next.js documentation and examples
        "https://github.com/microsoft/vscode-docs",  # VS Code documentation
        # Add your actual repository URLs here
    ]
    
    indexer = GitHubRepoIndexer()
    
    # Show current database stats
    try:
        conn = psycopg2.connect(**indexer.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        initial_count = cursor.fetchone()[0]
        print(f"📊 Current database: {initial_count} documents")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return
    
    # Index each repository
    total_indexed = 0
    for repo_url in repositories:
        if "github.com/user/" in repo_url:
            print("⚠️  Please update the repository URLs with actual user repositories!")
            break
            
        print(f"\n{'='*60}")
        indexed = indexer.index_repository(repo_url, max_files=30)
        total_indexed += indexed if indexed else 0
    
    # Show final stats
    try:
        conn = psycopg2.connect(**indexer.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        final_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"\n📊 Final database: {final_count} documents")
        print(f"📈 Total indexed: {total_indexed} files")
        print("\n🎉 Claude Desktop can now search GitHub repository content!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    main()
