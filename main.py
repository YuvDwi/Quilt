import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class GitHubCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Quilt API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
