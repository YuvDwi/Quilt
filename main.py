import os
import requests
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('deployments.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT NOT NULL,
            repo_url TEXT NOT NULL,
            user_id TEXT NOT NULL,
            sections_indexed INTEGER DEFAULT 0,
            deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

class GitHubCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Quilt API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

class DeployRequest(BaseModel):
    repo_url: str
    token: str
    user: str

@app.post("/auth/github/callback")
async def github_oauth_callback(request: GitHubCallbackRequest):
    """Handle GitHub OAuth callback"""
    github_client_id = os.getenv('GITHUB_CLIENT_ID')
    github_client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    
    if not github_client_id or not github_client_secret:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
    
    try:
        # Exchange code for access token
        token_response = requests.post('https://github.com/login/oauth/access_token', {
            'client_id': github_client_id,
            'client_secret': github_client_secret,
            'code': request.code
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

@app.post("/deploy")
async def deploy_repository(request: DeployRequest):
    """Deploy a repository and store in database"""
    try:
        # Extract repo name from URL
        repo_name = request.repo_url.split('/')[-1] if '/' in request.repo_url else request.repo_url
        
        # Mock processing - in real implementation, would parse repo content
        sections_indexed = 15  # Mock number
        
        # Store deployment in database
        conn = sqlite3.connect('deployments.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO deployments (repo_name, repo_url, user_id, sections_indexed)
            VALUES (?, ?, ?, ?)
        ''', (repo_name, request.repo_url, request.user, sections_indexed))
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Repository {repo_name} deployed successfully",
            "sections_indexed": sections_indexed,
            "user": request.user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

@app.get("/deployments/{username}")
async def get_deployments(username: str):
    """Get deployments for a user from database"""
    try:
        conn = sqlite3.connect('deployments.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT repo_name, repo_url, deployed_at, sections_indexed
            FROM deployments 
            WHERE user_id = ?
            ORDER BY deployed_at DESC
        ''', (username,))
        
        deployments = []
        for row in cursor.fetchall():
            deployments.append({
                "repo_name": row[0],
                "repo_url": row[1],
                "deployed_at": row[2],
                "sections_indexed": row[3]
            })
        
        conn.close()
        return {"deployments": deployments}
    except Exception as e:
        return {"deployments": []}

@app.get("/repositories")
async def get_repositories():
    """Get repositories (mock data for now)"""
    return {
        "repositories": [
            {
                "id": 1,
                "name": "sample-repo",
                "full_name": "YuvDwi/sample-repo",
                "html_url": "https://github.com/YuvDwi/sample-repo",
                "description": "Sample repository for testing",
                "updated_at": "2025-01-28T12:00:00Z",
                "private": False
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
