#!/usr/bin/env python3
"""
Cloud-optimized Quilt API for Render deployment
"""

import os
import json
import sqlite3
import psycopg2
import requests
import cohere
import numpy as np
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Quilt API - Cloud",
    description="Deploy repositories and index content for Claude Desktop search (Cloud Version)",
    version="2.0.0-cloud"
)

# CORS middleware for cloud deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class DeployRequest(BaseModel):
    user_id: str
    repo_url: str
    github_token: Optional[str] = None  # User's OAuth token

class GitHubCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

class ContentPreview(BaseModel):
    file_path: str
    content_type: str
    content_preview: str
    word_count: int
    section_title: str

class DeployResponse(BaseModel):
    success: bool
    message: str
    deployment_id: Optional[int] = None
    sections_indexed: Optional[int] = 0
    documents_added: Optional[int] = 0
    content_preview: Optional[List[ContentPreview]] = []
    total_files_processed: Optional[int] = 0

# Cloud-optimized Quilt Deployment Class
class CloudQuiltDeployment:
    def __init__(self):
        # Use environment variable for database URL (Render provides this)
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Parse database URL for connection parameters
        parsed = urlparse(self.database_url)
        self.pg_db_config = {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "database": parsed.path[1:],  # Remove leading slash
            "user": parsed.username,
            "password": parsed.password
        }
        
        # Initialize Cohere
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        self.cohere_client = cohere.Client(self.cohere_api_key) if self.cohere_api_key else None
        
        # Initialize GitHub
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_client_id = os.getenv('GITHUB_CLIENT_ID')
        self.github_client_secret = os.getenv('GITHUB_CLIENT_SECRET')
        
        # Initialize PostgreSQL tables
        self.init_postgres_tables()
        
        print("✅ Cloud Quilt Deployment initialized")
        print(f"📊 Database: {self.pg_db_config['host']}:{self.pg_db_config['port']}")
        print(f"🤖 Cohere: {'✅' if self.cohere_client else '❌'}")
        print(f"🐙 GitHub: {'✅' if self.github_token else '❌'}")
        print(f"🔑 OAuth: {'✅' if self.github_client_id and self.github_client_secret else '❌'}")

    def init_postgres_tables(self):
        """Initialize PostgreSQL tables"""
        try:
            with psycopg2.connect(**self.pg_db_config) as conn:
                with conn.cursor() as cursor:
                    # Create documents table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS documents (
                            id SERIAL PRIMARY KEY,
                            content TEXT NOT NULL,
                            embedding BYTEA,
                            doc_metadata JSONB,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        )
                    """)
                    
                    # Create deployments tracking table
                    cursor.execute("""
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
                    
                    conn.commit()
                    print("✅ PostgreSQL tables initialized")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            raise

    @contextmanager
    def get_pg_connection(self):
        """Get PostgreSQL connection with context manager"""
        conn = None
        try:
            conn = psycopg2.connect(**self.pg_db_config)
            yield conn
        finally:
            if conn:
                conn.close()

    def generate_embedding(self, text: str) -> Optional[bytes]:
        """Generate Cohere embedding"""
        if not self.cohere_client or not text.strip():
            return None
        
        try:
            response = self.cohere_client.embed(
                texts=[text],
                model='embed-english-v3.0',
                input_type='search_document'
            )
            embedding_array = np.array(response.embeddings[0], dtype=np.float32)
            return embedding_array.tobytes()
        except Exception as e:
            print(f"⚠️  Embedding error: {e}")
            return None

    def fetch_github_content(self, repo_url: str, user_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch content from GitHub repository"""
        try:
            # Parse GitHub URL
            if 'github.com' not in repo_url:
                raise ValueError("Invalid GitHub URL")
            
            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) < 2:
                raise ValueError("Invalid GitHub repository format")
            
            owner, repo = parts[0], parts[1]
            
            # GitHub API headers - prefer user token over service token
            headers = {}
            token_to_use = user_token or self.github_token
            if token_to_use:
                headers['Authorization'] = f'token {token_to_use}'
            
            # Get repository contents
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            contents = []
            files = response.json()
            
            for file_info in files:
                if file_info['type'] == 'file' and file_info['name'].endswith(('.html', '.jsx', '.tsx', '.js', '.ts')):
                    try:
                        # Download file content
                        file_response = requests.get(file_info['download_url'])
                        file_response.raise_for_status()
                        
                        content = file_response.text
                        
                        # Parse HTML/JSX content and extract only data-llm tagged elements
                        if file_info['name'].endswith(('.html', '.jsx', '.tsx')):
                            soup = BeautifulSoup(content, 'html.parser')
                            
                            # Find all elements with data-llm attributes
                            llm_elements = soup.find_all(attrs={'data-llm': True})
                            
                            for element in llm_elements:
                                llm_type = element.get('data-llm')
                                element_content = element.get_text(strip=True)
                                
                                if len(element_content) > 10:  # Only process substantial content
                                    contents.append({
                                        'content': element_content,
                                        'metadata': {
                                            'source': 'github_repo',
                                            'repo_name': f"{owner}/{repo}",
                                            'file_path': file_info['path'],
                                            'file_name': file_info['name'],
                                            'file_size': file_info['size'],
                                            'download_url': file_info['download_url'],
                                            'llm_type': llm_type,
                                            'element_tag': element.name
                                        }
                                    })
                        
                        # For JS/TS files, look for JSX-style data-llm attributes in strings
                        elif file_info['name'].endswith(('.js', '.ts')):
                            import re
                            # Look for JSX elements with data-llm attributes
                            jsx_pattern = r'<(\w+)[^>]*data-llm=["\']([^"\']+)["\'][^>]*>(.*?)</\1>'
                            matches = re.findall(jsx_pattern, content, re.DOTALL | re.IGNORECASE)
                            
                            for tag, llm_type, jsx_content in matches:
                                # Clean JSX content (remove nested tags)
                                clean_content = re.sub(r'<[^>]+>', '', jsx_content).strip()
                                clean_content = ' '.join(clean_content.split())
                                
                                if len(clean_content) > 10:
                                    contents.append({
                                        'content': clean_content,
                                        'metadata': {
                                            'source': 'github_repo',
                                            'repo_name': f"{owner}/{repo}",
                                            'file_path': file_info['path'],
                                            'file_name': file_info['name'],
                                            'file_size': file_info['size'],
                                            'download_url': file_info['download_url'],
                                            'llm_type': llm_type,
                                            'element_tag': tag
                                        }
                                    })
                    except Exception as e:
                        print(f"⚠️  Error processing {file_info['name']}: {e}")
                        continue
            
            return contents
            
        except Exception as e:
            print(f"❌ GitHub fetch error: {e}")
            return []

    def deploy_repository(self, user_id: str, repo_url: str, user_token: Optional[str] = None) -> Dict[str, Any]:
        """Deploy repository and index content"""
        try:
            # Extract repo name
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            
            print(f"🚀 Deploying {repo_name} for {user_id}")
            
            # Fetch GitHub content using user's token
            contents = self.fetch_github_content(repo_url, user_token)
            print(f"🔍 DEBUG: Fetched {len(contents) if contents else 0} content items")
            if contents:
                print(f"🔍 DEBUG: First content item keys: {list(contents[0].keys()) if contents else 'None'}")
            
            if not contents:
                return {
                    'success': False,
                    'message': 'No content found in repository',
                    'sections_indexed': 0
                }
            
            # Index content to PostgreSQL
            documents_added = 0
            
            with self.get_pg_connection() as conn:
                with conn.cursor() as cursor:
                    for item in contents:
                        try:
                            # Generate embedding
                            embedding = self.generate_embedding(item['content'])
                            
                            # Enhanced metadata
                            metadata = {
                                **item['metadata'],
                                'user_id': user_id,
                                'deployed_at': datetime.now().isoformat(),
                                'deployment_source': 'cloud_api'
                            }
                            
                            # Insert into PostgreSQL
                            cursor.execute(
                                """INSERT INTO documents (content, embedding, doc_metadata) 
                                   VALUES (%s, %s, %s)""",
                                (item['content'], embedding, json.dumps(metadata))
                            )
                            documents_added += 1
                            
                        except Exception as e:
                            print(f"⚠️  Error indexing content: {e}")
                            continue
                    
                    # Record deployment
                    cursor.execute(
                        """INSERT INTO deployments 
                           (user_id, repo_name, repo_url, sections_indexed, pg_documents_added) 
                           VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                        (user_id, repo_name, repo_url, len(contents), documents_added)
                    )
                    
                    deployment_id = cursor.fetchone()[0]
                    conn.commit()
            
            print(f"✅ Deployment complete: {documents_added} documents indexed")
            print(f"📋 Total content sections: {len(contents)}")
            
            # Get a preview of the indexed content
            content_preview = []
            for content in contents[:5]:  # Show first 5 sections as preview
                metadata = content.get("metadata", {})
                content_text = content.get("content", "")
                file_path = metadata.get("file_path", "Unknown")
                
                llm_type = metadata.get("llm_type", "content")
                element_tag = metadata.get("element_tag", "div")
                
                content_preview.append({
                    "file_path": file_path,
                    "content_type": metadata.get("file_name", "").split(".")[-1] if "." in metadata.get("file_name", "") else "html",
                    "content_preview": content_text[:200] + "..." if len(content_text) > 200 else content_text,
                    "word_count": len(content_text.split()),
                    "section_title": f"{llm_type.title()} ({element_tag}) - {metadata.get('file_name', 'Unknown')}"
                })

            response_data = {
                'success': True,
                'message': f'Successfully deployed {repo_name}',
                'deployment_id': deployment_id,
                'sections_indexed': len(contents),
                'documents_added': documents_added,
                'content_preview': content_preview,
                'total_files_processed': len(set(content.get("metadata", {}).get("file_path", "") for content in contents))
            }
            
            return response_data
            
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return {
                'success': False,
                'message': f'Deployment failed: {str(e)}',
                'sections_indexed': 0
            }

    def get_user_deployments(self, user_id: str) -> List[Dict[str, Any]]:
        """Get deployments for a user"""
        try:
            with self.get_pg_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """SELECT id, repo_name, repo_url, deployed_at, status, 
                                  sections_indexed, pg_documents_added 
                           FROM deployments 
                           WHERE user_id = %s 
                           ORDER BY deployed_at DESC""",
                        (user_id,)
                    )
                    
                    deployments = []
                    for row in cursor.fetchall():
                        deployments.append({
                            'id': row[0],
                            'repo_name': row[1],
                            'repo_url': row[2],
                            'deployed_at': row[3].isoformat() if row[3] else None,
                            'status': row[4],
                            'sections_indexed': row[5],
                            'documents_added': row[6]
                        })
                    
                    return deployments
                    
        except Exception as e:
            print(f"❌ Error fetching deployments: {e}")
            return []

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_pg_connection() as conn:
                with conn.cursor() as cursor:
                    # Total documents
                    cursor.execute("SELECT COUNT(*) FROM documents")
                    total_docs = cursor.fetchone()[0]
                    
                    # Documents by repo
                    cursor.execute("""
                        SELECT doc_metadata->>'repo_name' as repo, COUNT(*) as count
                        FROM documents 
                        WHERE doc_metadata->>'repo_name' IS NOT NULL
                        GROUP BY doc_metadata->>'repo_name'
                        ORDER BY count DESC
                    """)
                    
                    repos = {}
                    for row in cursor.fetchall():
                        repos[row[0]] = row[1]
                    
                    return {
                        'total_documents': total_docs,
                        'repositories': repos,
                        'database_connected': True
                    }
                    
        except Exception as e:
            print(f"❌ Stats error: {e}")
            return {
                'total_documents': 0,
                'repositories': {},
                'database_connected': False,
                'error': str(e)
            }

# Initialize deployment system
deployment_system = CloudQuiltDeployment()

# API Routes
@app.get("/")
async def root():
    return {
        "name": "Quilt API - Cloud",
        "version": "2.0.0-cloud",
        "description": "Deploy repositories and index content for Claude Desktop search (Cloud Version)",
        "features": [
            "GitHub repository deployment",
            "Automatic PostgreSQL indexing", 
            "Claude Desktop search integration",
            "Cohere embeddings generation",
            "Cloud-hosted on Render"
        ],
        "endpoints": {
            "deploy": "/deploy",
            "deployments": "/deployments/<user>",
            "stats": "/stats",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    stats = deployment_system.get_database_stats()
    return {
        "status": "healthy",
        "postgres": "connected" if stats['database_connected'] else "disconnected",
        "documents_indexed": stats['total_documents'],
        "cohere_api": "configured" if deployment_system.cohere_client else "missing",
        "github_api": "configured" if deployment_system.github_token else "missing"
    }

@app.get("/stats")
async def get_stats():
    return deployment_system.get_database_stats()

@app.post("/deploy", response_model=DeployResponse)
async def deploy_repository(request: DeployRequest, background_tasks: BackgroundTasks):
    try:
        result = deployment_system.deploy_repository(
            request.user_id, 
            request.repo_url, 
            request.github_token
        )
        
        return DeployResponse(
            success=result['success'],
            message=result['message'],
            deployment_id=result.get('deployment_id'),
            sections_indexed=result.get('sections_indexed', 0),
            documents_added=result.get('documents_added', 0),
            content_preview=result.get('content_preview', []),
            total_files_processed=result.get('total_files_processed', 0)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

@app.get("/deployments/{user_id}")
async def get_deployments(user_id: str):
    try:
        deployments = deployment_system.get_user_deployments(user_id)
        return {
            "user_id": user_id,
            "deployments": deployments,
            "total": len(deployments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch deployments: {str(e)}")

@app.post("/auth/github/callback")
async def github_oauth_callback(request: GitHubCallbackRequest):
    """Handle GitHub OAuth callback and exchange code for access token"""
    try:
        if not deployment_system.github_client_id or not deployment_system.github_client_secret:
            raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
        
        # Exchange authorization code for access token
        token_url = "https://github.com/login/oauth/access_token"
        token_data = {
            "client_id": deployment_system.github_client_id,
            "client_secret": deployment_system.github_client_secret,
            "code": request.code
        }
        
        token_headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        if "access_token" not in token_json:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        access_token = token_json["access_token"]
        
        # Get user information
        user_url = "https://api.github.com/user"
        user_headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/json"
        }
        
        user_response = requests.get(user_url, headers=user_headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        return {
            "access_token": access_token,
            "user": {
                "login": user_data.get("login"),
                "id": user_data.get("id"),
                "name": user_data.get("name"),
                "avatar_url": user_data.get("avatar_url")
            }
        }
        
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
