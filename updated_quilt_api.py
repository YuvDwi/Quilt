#!/usr/bin/env python3
"""
Updated Quilt API with PostgreSQL Integration
Automatically indexes deployed repositories into PostgreSQL for Claude Desktop search
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from integrated_quilt_deployer import IntegratedQuiltDeployer

app = FastAPI(title="Quilt API", description="Deploy repositories and index content for Claude Desktop search")

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

# Initialize the integrated deployer
deployer = IntegratedQuiltDeployer()

class DeployRequest(BaseModel):
    repo_url: str
    token: str
    user: str

class GitHubCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

@app.get("/")
async def root():
    """API status and information"""
    return {
        "name": "Quilt API",
        "version": "2.0.0",
        "description": "Deploy repositories and index content for Claude Desktop search",
        "features": [
            "GitHub repository deployment",
            "Automatic PostgreSQL indexing", 
            "Claude Desktop search integration",
            "Cohere embeddings generation"
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
    """Health check endpoint"""
    try:
        # Test PostgreSQL connection
        import psycopg2
        conn = psycopg2.connect(**deployer.pg_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_docs = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "postgres": "connected",
            "documents_indexed": total_docs,
            "cohere_api": "configured" if deployer.cohere_client else "not configured"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/deploy")
async def deploy_repo(request: DeployRequest):
    """Deploy and index a repository into PostgreSQL for Claude Desktop search"""
    print(f"🚀 Deploy request: {request.repo_url} for user {request.user}")
    
    result = deployer.deploy_repository(request.user, request.repo_url, request.token)
    
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result['error'])
    
    # Add Claude Desktop search info to response
    result['claude_search'] = True
    result['claude_message'] = "Content is now searchable via Claude Desktop!"
    
    return result

@app.get("/deployments/{user}")
async def get_deployments(user: str):
    """Get user's deployments"""
    deployments = deployer.get_deployments(user)
    
    return {
        'deployments': deployments,
        'total': len(deployments),
        'claude_search_enabled': True
    }

@app.get("/stats")
async def get_stats():
    """Get deployment and indexing statistics"""
    try:
        # Get deployment stats from SQLite
        import sqlite3
        with sqlite3.connect(deployer.db_path) as conn:
            # Total deployments
            cursor = conn.execute("SELECT COUNT(*) FROM deployments")
            total_deployments = cursor.fetchone()[0]
            
            # Total sections indexed
            cursor = conn.execute("SELECT SUM(pg_documents_added) FROM deployments")
            total_sections = cursor.fetchone()[0] or 0
            
            # Unique users
            cursor = conn.execute("SELECT COUNT(DISTINCT user_id) FROM deployments")
            unique_users = cursor.fetchone()[0]
            
            # Recent deployments
            cursor = conn.execute("""
                SELECT repo_name, user_id, deployed_at, pg_documents_added 
                FROM deployments 
                ORDER BY deployed_at DESC 
                LIMIT 10
            """)
            recent_deployments = [
                {
                    'repo_name': row[0],
                    'user': row[1],
                    'deployed_at': row[2],
                    'documents_added': row[3]
                }
                for row in cursor.fetchall()
            ]
        
        # Get PostgreSQL stats
        import psycopg2
        with psycopg2.connect(**deployer.pg_config) as pg_conn:
            cursor = pg_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_postgres_docs = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM documents 
                WHERE doc_metadata->>'source' = 'quilt_deployment'
            """)
            quilt_docs = cursor.fetchone()[0]
        
        return {
            'total_deployments': total_deployments,
            'total_sections_indexed': total_sections,
            'unique_users': unique_users,
            'recent_deployments': recent_deployments,
            'postgres_total_documents': total_postgres_docs,
            'postgres_quilt_documents': quilt_docs,
            'claude_desktop_ready': True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@app.post("/auth/github/callback")
async def github_oauth_callback(request: GitHubCallbackRequest):
    """Handle GitHub OAuth callback"""
    code = request.code
    
    # Exchange code for token
    client_id = os.getenv('GITHUB_CLIENT_ID')
    client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
    
    import requests
    
    token_url = "https://github.com/login/oauth/access_token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code
    }
    
    headers = {'Accept': 'application/json'}
    response = requests.post(token_url, data=token_data, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    token_info = response.json()
    access_token = token_info.get('access_token')
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")
    
    # Get user info
    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'token {access_token}'}
    )
    
    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info")
    
    user_info = user_response.json()
    
    return {
        'access_token': access_token,
        'user': user_info['login'],
        'user_info': user_info
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Quilt API with PostgreSQL Integration")
    print("✨ Features:")
    print("  - Deploy GitHub repositories")
    print("  - Automatic PostgreSQL indexing")
    print("  - Claude Desktop search integration")
    print("  - Cohere embeddings generation")
    print()
    print("🔗 Access: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    
    uvicorn.run("updated_quilt_api:app", host="0.0.0.0", port=8000, reload=True)
