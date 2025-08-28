#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import sqlite3
from datetime import datetime
import os

from lightweight_search import LightweightSearchEngine

app = FastAPI(title="Quilt API", description="Centralized vector database for web content")

search_engine = LightweightSearchEngine()

QUILT_DB_PATH = "quilt_repositories.db"

def init_quilt_database():
    with sqlite3.connect(QUILT_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY,
                full_name TEXT UNIQUE NOT NULL,
                owner TEXT NOT NULL,
                source_url TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_sections INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS content_sections (
                id INTEGER PRIMARY KEY,
                repository_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_file TEXT,
                github_url TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (repository_id) REFERENCES repositories (id)
            )
        """)
        
        conn.execute("CREATE INDEX IF NOT EXISTS idx_repo_name ON repositories(full_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_repo_owner ON repositories(owner)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_section_title ON content_sections(title)")

init_quilt_database()

class RepositoryIndexRequest(BaseModel):
    repository: str
    owner: str
    source_url: str
    indexed_at: str
    sections: List[Dict[str, Any]]
    total_sections: int

class SearchRequest(BaseModel):
    query: str
    repository_filter: Optional[str] = None
    owner_filter: Optional[str] = None
    max_results: int = 10
    search_type: str = "hybrid"

@app.post("/index/repository")
async def index_repository(request: RepositoryIndexRequest):
    try:
        with sqlite3.connect(QUILT_DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT id, total_sections FROM repositories WHERE full_name = ?",
                (request.repository,)
            )
            existing_repo = cursor.fetchone()
            
            if existing_repo:
                repo_id, old_sections = existing_repo
                conn.execute("""
                    UPDATE repositories 
                    SET last_updated = ?, total_sections = ?
                    WHERE id = ?
                """, (datetime.utcnow(), request.total_sections, repo_id))
                
                conn.execute("DELETE FROM content_sections WHERE repository_id = ?", (repo_id,))
            else:
                cursor = conn.execute("""
                    INSERT INTO repositories (full_name, owner, source_url, indexed_at, total_sections)
                    VALUES (?, ?, ?, ?, ?)
                """, (request.repository, request.owner, request.source_url, 
                      request.indexed_at, request.total_sections))
                repo_id = cursor.lastrowid
            
            for section in request.sections:
                metadata = section.get('metadata', {})
                
                search_engine.add_document(
                    content=section['content'],
                    metadata={
                        'title': section['title'],
                        'repository': request.repository,
                        'owner': request.owner,
                        'source_file': metadata.get('source_file', ''),
                        'github_url': metadata.get('github_url', ''),
                        'type': 'quilt_indexed',
                        'indexed_at': request.indexed_at
                    }
                )
                
                conn.execute("""
                    INSERT INTO content_sections (repository_id, title, content, source_file, github_url, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    repo_id,
                    section['title'],
                    section['content'],
                    metadata.get('source_file', ''),
                    metadata.get('github_url', ''),
                    json.dumps(metadata)
                ))
            
            conn.commit()
            
            return {
                "message": "Repository indexed successfully",
                "repository": request.repository,
                "sections_indexed": len(request.sections),
                "total_sections": request.total_sections
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing repository: {str(e)}")

@app.get("/search")
async def search_content(
    query: str,
    repository_filter: Optional[str] = None,
    owner_filter: Optional[str] = None,
    max_results: int = 10,
    search_type: str = "hybrid"
):
    try:
        if search_type == "vector":
            results = search_engine.search_similar(query, k=max_results*2)
        elif search_type == "hybrid":
            results = search_engine.hybrid_search(query, k=max_results*2)
        else:
            results = search_engine.search_similar(query, k=max_results*2)
        
        filtered_results = []
        for result in results:
            metadata = result.get('metadata', {})
            
            if repository_filter and metadata.get('repository') != repository_filter:
                continue
            if owner_filter and metadata.get('owner') != owner_filter:
                continue
            
            filtered_results.append(result)
            
            if len(filtered_results) >= max_results:
                break
        
        return {
            "query": query,
            "search_type": search_type,
            "filters": {
                "repository": repository_filter,
                "owner": owner_filter
            },
            "total_results": len(filtered_results),
            "results": filtered_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/repositories")
async def list_repositories():
    try:
        with sqlite3.connect(QUILT_DB_PATH) as conn:
            cursor = conn.execute("""
                SELECT full_name, owner, source_url, indexed_at, last_updated, total_sections, status
                FROM repositories
                ORDER BY last_updated DESC
            """)
            
            repositories = []
            for row in cursor.fetchall():
                repositories.append({
                    "full_name": row[0],
                    "owner": row[1],
                    "source_url": row[2],
                    "indexed_at": row[3],
                    "last_updated": row[4],
                    "total_sections": row[5],
                    "status": row[6]
                })
            
            return {
                "total_repositories": len(repositories),
                "repositories": repositories
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing repositories: {str(e)}")

@app.get("/repository/{owner}/{repo}")
async def get_repository_details(owner: str, repo: str):
    try:
        full_name = f"{owner}/{repo}"
        
        with sqlite3.connect(QUILT_DB_PATH) as conn:
            cursor = conn.execute("""
                SELECT full_name, owner, source_url, indexed_at, last_updated, total_sections, status
                FROM repositories
                WHERE full_name = ?
            """, (full_name,))
            
            repo_info = cursor.fetchone()
            if not repo_info:
                raise HTTPException(status_code=404, detail="Repository not found")
            
            cursor = conn.execute("""
                SELECT title, source_file, github_url, indexed_at
                FROM content_sections cs
                JOIN repositories r ON cs.repository_id = r.id
                WHERE r.full_name = ?
                ORDER BY cs.indexed_at DESC
            """, (full_name,))
            
            sections = []
            for row in cursor.fetchall():
                sections.append({
                    "title": row[0],
                    "source_file": row[1],
                    "github_url": row[2],
                    "indexed_at": row[3]
                })
            
            return {
                "repository": {
                    "full_name": repo_info[0],
                    "owner": repo_info[1],
                    "source_url": repo_info[2],
                    "indexed_at": repo_info[3],
                    "last_updated": repo_info[4],
                    "total_sections": repo_info[5],
                    "status": repo_info[6]
                },
                "sections": sections
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting repository details: {str(e)}")

@app.get("/stats")
async def get_quilt_stats():
    try:
        with sqlite3.connect(QUILT_DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM repositories")
            total_repos = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM content_sections")
            total_sections = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT SUM(total_sections) FROM repositories")
            total_indexed = cursor.fetchone()[0] or 0
            
            cursor = conn.execute("SELECT owner, COUNT(*) FROM repositories GROUP BY owner")
            owners = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total_repositories": total_repos,
                "total_content_sections": total_sections,
                "total_indexed_sections": total_indexed,
                "unique_owners": len(owners),
                "owners": owners,
                "search_engine_documents": len(search_engine.list_documents()['documents'])
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "Quilt API",
        "search_engine": "connected",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
