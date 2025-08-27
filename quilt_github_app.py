#!/usr/bin/env python3

import os
import jwt
import time
import requests
import json
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import hmac
import hashlib
from pathlib import Path
import tempfile
import shutil

from simple_parser import EnhancedHTMLParser
import config

class QuiltGitHubApp:
    def __init__(self, app_id: str, private_key_path: str, installation_id: Optional[str] = None):
        self.app_id = app_id
        self.private_key_path = private_key_path
        self.installation_id = installation_id
        self.base_url = "https://api.github.com"
        
        with open(private_key_path, 'r') as key_file:
            self.private_key = key_file.read()
        
        self.html_parser = EnhancedHTMLParser()
        
        self.quilt_api_url = os.getenv('QUILT_API_URL', 'http://localhost:8000')
        self.quilt_api_key = os.getenv('QUILT_API_KEY', '')
    
    def generate_jwt(self) -> str:
        now = int(time.time())
        payload = {
            'iat': now,
            'exp': now + (10 * 60),
            'iss': self.app_id
        }
        
        token = jwt.encode(payload, self.private_key, algorithm='RS256')
        return token
    
    def get_installation_token(self, installation_id: Optional[str] = None) -> str:
        if installation_id:
            self.installation_id = installation_id
        
        if not self.installation_id:
            raise ValueError("Installation ID is required")
        
        jwt_token = self.generate_jwt()
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f"{self.base_url}/app/installations/{self.installation_id}/access_tokens"
        response = requests.post(url, headers=headers)
        
        if response.status_code == 201:
            return response.json()['token']
        else:
            raise Exception(f"Failed to get installation token: {response.status_code} - {response.text}")
    
    def get_repository_contents(self, owner: str, repo: str, path: str = "", ref: str = "main") -> List[Dict[str, Any]]:
        token = self.get_installation_token()
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {'ref': ref}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to get repository contents: {response.status_code}")
        
        contents = response.json()
        files = []
        
        if isinstance(contents, list):
            for item in contents:
                if item['type'] == 'file':
                    if item['name'].endswith('.html') or item['name'].endswith('.htm'):
                        files.append(item)
                elif item['type'] == 'dir':
                    sub_files = self.get_repository_contents(owner, repo, item['path'], ref)
                    files.extend(sub_files)
        
        return files
    
    def download_file_content(self, owner: str, repo: str, file_path: str, ref: str = "main") -> str:
        token = self.get_installation_token()
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        params = {'ref': ref}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to download file: {response.status_code}")
        
        content_data = response.json()
        if 'content' in content_data:
            content = base64.b64decode(content_data['content']).decode('utf-8')
            return content
        else:
            raise Exception("No content found in file")
    
    def process_html_file(self, html_content: str, file_path: str, repo_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
            temp_file.write(html_content)
            temp_file_path = temp_file.name
        
        try:
            pairs = self.html_parser.parse_html_file(temp_file_path)
            
            enriched_pairs = []
            for pair in pairs:
                enriched_pair = {
                    **pair,
                    'metadata': {
                        'title': pair['title'],
                        'source_file': file_path,
                        'repository': repo_info['full_name'],
                        'owner': repo_info['owner']['login'],
                        'type': 'html_section',
                        'indexed_at': datetime.utcnow().isoformat(),
                        'github_url': f"https://github.com/{repo_info['full_name']}/blob/main/{file_path}",
                        'title_length': len(pair['title']),
                        'content_length': len(pair['content'])
                    }
                }
                enriched_pairs.append(enriched_pair)
            
            return enriched_pairs
            
        finally:
            os.unlink(temp_file_path)
    
    def push_to_quilt_database(self, pairs: List[Dict[str, Any]], repo_info: Dict[str, Any]) -> bool:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.quilt_api_key}'
        }
        
        quilt_data = {
            'repository': repo_info['full_name'],
            'owner': repo_info['owner']['login'],
            'source_url': repo_info['html_url'],
            'indexed_at': datetime.utcnow().isoformat(),
            'sections': pairs,
            'total_sections': len(pairs)
        }
        
        try:
            response = requests.post(
                f"{self.quilt_api_url}/index/repository",
                headers=headers,
                json=quilt_data
            )
            
            if response.status_code == 200:
                print(f"Successfully indexed {len(pairs)} sections from {repo_info['full_name']}")
                return True
            else:
                print(f"Failed to index repository: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error pushing to Quilt database: {e}")
            return False
    
    def index_repository(self, owner: str, repo: str, ref: str = "main") -> Dict[str, Any]:
        print(f"Indexing repository: {owner}/{repo}")
        
        try:
            token = self.get_installation_token()
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            repo_response = requests.get(repo_url, headers=headers)
            if repo_response.status_code != 200:
                raise Exception(f"Failed to get repository info: {repo_response.status_code}")
            
            repo_info = repo_response.json()
            
            html_files = self.get_repository_contents(owner, repo, "", ref)
            print(f"Found {len(html_files)} HTML files")
            
            all_pairs = []
            processed_files = 0
            
            for file_info in html_files:
                try:
                    html_content = self.download_file_content(owner, repo, file_info['path'], ref)
                    
                    pairs = self.process_html_file(html_content, file_info['path'], repo_info)
                    
                    if pairs:
                        all_pairs.extend(pairs)
                        processed_files += 1
                        print(f"Processed {file_info['path']}: {len(pairs)} sections")
                    
                except Exception as e:
                    print(f"Error processing {file_info['path']}: {e}")
                    continue
            
            if all_pairs:
                success = self.push_to_quilt_database(all_pairs, repo_info)
                if success:
                    print(f"Successfully indexed {len(all_pairs)} sections from {processed_files} files")
                else:
                    print("Failed to push to Quilt database")
            
            return {
                'repository': repo_info['full_name'],
                'html_files_found': len(html_files),
                'files_processed': processed_files,
                'sections_indexed': len(all_pairs),
                'success': len(all_pairs) > 0
            }
            
        except Exception as e:
            print(f"Error indexing repository: {e}")
            return {
                'repository': f"{owner}/{repo}",
                'error': str(e),
                'success': False
            }

app = FastAPI()

quilt_app = QuiltGitHubApp(
    app_id=config.GITHUB_APP_ID,
    private_key_path=config.PRIVATE_KEY_PATH,
    installation_id=config.INSTALLATION_ID
)

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected_signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@app.post("/webhook")
async def handle_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    payload = await request.body()
    
    if not verify_webhook_signature(payload, x_hub_signature_256, config.WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    try:
        event_data = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    event_type = x_github_event
    
    if event_type == "push":
        return await handle_push_event(event_data)
    else:
        return JSONResponse(content={"message": f"Event {x_github_event} received"}, status_code=200)

async def handle_push_event(event_data: Dict[str, Any]) -> JSONResponse:
    repository = event_data.get("repository", {})
    ref = event_data.get("ref", "").replace("refs/heads/", "")
    
    if not repository or not ref:
        return JSONResponse(content={"message": "Invalid push event data"}, status_code=400)
    
    owner = repository["owner"]["login"]
    repo_name = repository["name"]
    
    print(f"Push event detected for {owner}/{repo_name} on branch {ref}")
    
    try:
        result = quilt_app.index_repository(owner, repo_name, ref)
        
        return JSONResponse(content={
            "message": "Repository indexing completed",
            "result": result
        }, status_code=200)
        
    except Exception as e:
        print(f"Error handling push event: {e}")
        return JSONResponse(content={
            "message": "Error indexing repository",
            "error": str(e)
        }, status_code=500)

@app.post("/index/repository")
async def manual_index_repository(owner: str, repo: str, ref: str = "main"):
    try:
        result = quilt_app.index_repository(owner, repo, ref)
        return {"message": "Repository indexing completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": "Quilt GitHub App"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
