#!/usr/bin/env python3

import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Prevents startup issues
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations for faster startup

import requests
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
import zipfile
from pathlib import Path
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import heavy modules only when needed
def get_html_parser():
    from simple_parser import EnhancedHTMLParser
    return EnhancedHTMLParser()

def get_vector_search():
    try:
        from hybrid_vector_search import HybridVectorSearch
        return HybridVectorSearch()
    except Exception as e:
        print(f"Warning: Could not initialize vector search: {e}")
        return None

app = FastAPI(title="Quilt React API", description="Backend API for Quilt React deployment interface")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",   # Vercel deployment
        "https://your-frontend-domain.vercel.app"  # Replace with your actual domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DeployRequest(BaseModel):
    repo_url: str
    token: str
    user: str

class QuiltDeployment:
    def __init__(self):
        # Don't initialize any heavy modules during startup
        self.html_parser = None
        self.vector_search = None
        self.db_path = "quilt_deployments.db"
        self.init_database()
    
    def get_html_parser(self):
        """Lazy initialization of HTML parser"""
        if self.html_parser is None:
            try:
                self.html_parser = get_html_parser()
                print("✅ HTML Parser initialized")
            except Exception as e:
                print(f"⚠️ HTML Parser initialization failed: {e}")
                # Create dummy parser
                class DummyParser:
                    def parse_html_file(self, file_path):
                        return []
                    def add_document(self, content, metadata=None):
                        pass
                self.html_parser = DummyParser()
        return self.html_parser
    
    def get_vector_search(self):
        """Lazy initialization of vector search"""
        if self.vector_search is None:
            try:
                self.vector_search = get_vector_search()
                print("✅ Vector search initialized")
            except Exception as e:
                print(f"⚠️ Vector search initialization failed: {e}")
                # Create a dummy object for fallback
                class DummyVectorSearch:
                    def search_similar(self, query, k=5):
                        return []
                    def keyword_search(self, query, k=5):
                        return []
                    def vector_search(self, query, k=5):
                        return []
                    def add_document(self, content, metadata=None):
                        pass
                self.vector_search = DummyVectorSearch()
        return self.vector_search
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    repo_name TEXT NOT NULL,
                    repo_url TEXT NOT NULL,
                    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'deployed',
                    sections_indexed INTEGER DEFAULT 0
                )
            """)
    
    def deploy_repository(self, user_id: str, repo_url: str, access_token: str) -> Dict[str, Any]:
        """Download and index a repository"""
        try:
            # Extract owner/repo from URL
            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) < 2:
                raise Exception("Invalid repository URL")
            
            owner, repo = parts[0], parts[1]
            
            # Download repository as ZIP
            download_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/main"
            headers = {'Authorization': f'token {access_token}'}
            
            response = requests.get(download_url, headers=headers)
            if response.status_code != 200:
                # Try 'master' branch if 'main' fails
                download_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/master"
                response = requests.get(download_url, headers=headers)
                if response.status_code != 200:
                    raise Exception(f"Failed to download repository: {response.status_code}")
            
            # Extract and process HTML files
            sections_indexed = 0
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = Path(temp_dir) / "repo.zip"
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find and process HTML files
                for html_file in Path(temp_dir).rglob("*.html"):
                    try:
                        html_parser = self.get_html_parser()
                        pairs = html_parser.parse_html_file(str(html_file))
                        for pair in pairs:
                            html_parser.add_document(
                                f"{pair['title']}: {pair['content']}", 
                                {
                                    'repository': f"{owner}/{repo}",
                                    'file': str(html_file.name),
                                    'type': 'html_section',
                                    'user': user_id
                                }
                            )
                            sections_indexed += 1
                    except Exception as e:
                        print(f"Error processing {html_file}: {e}")
            
            # Record deployment
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO deployments (user_id, repo_name, repo_url, sections_indexed) VALUES (?, ?, ?, ?)",
                    (user_id, f"{owner}/{repo}", repo_url, sections_indexed)
                )
            
            return {
                'status': 'success',
                'repository': f"{owner}/{repo}",
                'sections_indexed': sections_indexed
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

deployer = QuiltDeployment()

# Mount static files if directory exists
import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Serve the main HTML page or API info"""
    if os.path.exists("static/index.html"):
        return FileResponse('static/index.html')
    else:
        return {
            "message": "Quilt API is running",
            "version": "1.0.0",
            "endpoints": {
                "api_status": "/api",
                "search": "/search?query=<query>&search_type=<hybrid|vector|keyword>",
                "deploy": "/deploy",
                "deployments": "/deployments/<user>",
                "stats": "/stats"
            }
        }

@app.get("/api")
async def api_status():
    """API status endpoint"""
    return {
        "message": "Quilt React API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Simple health check endpoint - no heavy operations"""
    return {
        "status": "healthy", 
        "port": os.getenv("PORT", "8005"),
        "message": "API is running",
        "timestamp": str(datetime.now())
    }

@app.post("/deploy")
async def deploy_repo(request: DeployRequest):
    """Deploy and index a repository"""
    result = deployer.deploy_repository(request.user, request.repo_url, request.token)
    
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result

@app.get("/deployments/{user}")
async def get_deployments(user: str):
    """Get user's deployments"""
    with sqlite3.connect(deployer.db_path) as conn:
        cursor = conn.execute(
            "SELECT repo_name, repo_url, deployed_at, sections_indexed FROM deployments WHERE user_id = ? ORDER BY deployed_at DESC",
            (user,)
        )
        deployments = [
            {
                'repo_name': row[0],
                'repo_url': row[1], 
                'deployed_at': row[2],
                'sections_indexed': row[3]
            }
            for row in cursor.fetchall()
        ]
    
    return {'deployments': deployments}

@app.get("/search")
async def search_content(query: str, search_type: str = "hybrid", max_results: int = 10):
    """Search indexed content"""
    try:
        vector_search = deployer.get_vector_search()
        if search_type == "vector":
            results = vector_search.search_similar(query, k=max_results)
        elif search_type == "keyword":
            results = vector_search.keyword_search(query, k=max_results)
        else:  # hybrid
            results = vector_search.search_similar(query, k=max_results)
        
        return {
            "query": query,
            "search_type": search_type,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get deployment statistics"""
    with sqlite3.connect(deployer.db_path) as conn:
        # Total deployments
        cursor = conn.execute("SELECT COUNT(*) FROM deployments")
        total_deployments = cursor.fetchone()[0]
        
        # Total sections indexed
        cursor = conn.execute("SELECT SUM(sections_indexed) FROM deployments")
        total_sections = cursor.fetchone()[0] or 0
        
        # Unique users
        cursor = conn.execute("SELECT COUNT(DISTINCT user_id) FROM deployments")
        unique_users = cursor.fetchone()[0]
        
        # Recent deployments
        cursor = conn.execute("SELECT repo_name, user_id, deployed_at FROM deployments ORDER BY deployed_at DESC LIMIT 10")
        recent_deployments = [
            {
                'repo_name': row[0],
                'user': row[1],
                'deployed_at': row[2]
            }
            for row in cursor.fetchall()
        ]
    
    return {
        'total_deployments': total_deployments,
        'total_sections_indexed': total_sections,
        'unique_users': unique_users,
        'recent_deployments': recent_deployments
    }

class GitHubCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

@app.post("/auth/github/callback")
async def github_oauth_callback(request: GitHubCallbackRequest):
    """Handle GitHub OAuth callback securely on backend"""
    code = request.code
    state = request.state
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")
    
    # Exchange code for access token
    github_client_id = os.getenv('GITHUB_CLIENT_ID')
    github_client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    
    if not github_client_id or not github_client_secret:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
    
    try:
        # Exchange code for access token
        token_response = requests.post('https://github.com/login/oauth/access_token', {
            'client_id': github_client_id,
            'client_secret': github_client_secret,
            'code': code
        }, headers={'Accept': 'application/json'})
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Get user info
        user_response = requests.get('https://api.github.com/user', 
                                   headers={'Authorization': f'token {access_token}'})
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_data = user_response.json()
        
        return {
            'access_token': access_token,
            'user': user_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
