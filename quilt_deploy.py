#!/usr/bin/env python3

import os
import requests
import json
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from urllib.parse import urlencode
import tempfile
import zipfile
from pathlib import Path
from simple_parser import EnhancedHTMLParser
from hybrid_vector_search import HybridVectorSearch
import sqlite3
from typing import List, Dict, Any, Optional

app = FastAPI(title="Quilt Deploy", description="Deploy and index your repositories with Quilt")
templates = Jinja2Templates(directory="templates")

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', 'your_client_id')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', 'your_client_secret')
GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI', 'https://quilt-production.up.railway.app/auth/callback')

class QuiltDeployment:
    def __init__(self):
        self.html_parser = EnhancedHTMLParser()
        self.vector_search = HybridVectorSearch()
        self.db_path = "quilt_deployments.db"
        self.init_database()
    
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
            owner, repo = parts[0], parts[1]
            
            # Download repository as ZIP
            download_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/main"
            headers = {'Authorization': f'token {access_token}'}
            
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
                        pairs = self.html_parser.parse_html_file(str(html_file))
                        for pair in pairs:
                            self.html_parser.add_document(
                                f"{pair['title']}: {pair['content']}", 
                                {
                                    'repository': f"{owner}/{repo}",
                                    'file': str(html_file.name),
                                    'type': 'html_section'
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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with GitHub login"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/auth/login")
async def github_login():
    """Redirect to GitHub OAuth"""
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'redirect_uri': GITHUB_REDIRECT_URI,
        'scope': 'repo',
        'state': 'random_state_string'
    }
    url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url)

@app.get("/auth/callback")
async def github_callback(code: str, state: str):
    """Handle GitHub OAuth callback"""
    # Exchange code for access token
    token_data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://github.com/login/oauth/access_token',
            data=token_data,
            headers={'Accept': 'application/json'}
        )
    
    token_info = response.json()
    access_token = token_info.get('access_token')
    
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    
    # Get user info
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            'https://api.github.com/user',
            headers={'Authorization': f'token {access_token}'}
        )
    
    user_info = user_response.json()
    
    # Redirect to dashboard with token (in real app, use secure session)
    return RedirectResponse(f"/dashboard?token={access_token}&user={user_info['login']}")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, token: str, user: str):
    """User dashboard to select repositories"""
    # Get user's repositories
    async with httpx.AsyncClient() as client:
        repos_response = await client.get(
            'https://api.github.com/user/repos',
            headers={'Authorization': f'token {token}'}
        )
    
    repositories = repos_response.json()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "token": token,
        "repositories": repositories
    })

@app.post("/deploy")
async def deploy_repo(repo_url: str, token: str, user: str):
    """Deploy and index a repository"""
    result = deployer.deploy_repository(user, repo_url, token)
    return result

@app.get("/deployments/{user}")
async def get_deployments(user: str):
    """Get user's deployments"""
    with sqlite3.connect(deployer.db_path) as conn:
        cursor = conn.execute(
            "SELECT repo_name, repo_url, deployed_at, sections_indexed FROM deployments WHERE user_id = ?",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
