#!/usr/bin/env python3
"""
Remote MCP Server Setup for Cloud Deployment
This version can be deployed to any cloud service and accessed by ChatGPT Desktop
"""

import os
import asyncio
import json
import psycopg2
from typing import List, Dict, Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent
import mcp.types as types
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remote-database-mcp")

class RemoteDatabaseMCPServer:
    def __init__(self):
        self.server = Server("remote-database-search")
        
        # Database configuration from environment variables
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "quilt_embeddings"),
            "user": os.getenv("DB_USER", "quilt_user"),
            "password": os.getenv("DB_PASSWORD", "your_secure_password")
        }
        
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [
                Tool(
                    name="search_database",
                    description="Search the remote PostgreSQL database for content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum results (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_stats",
                    description="Get database statistics",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            try:
                if name == "search_database":
                    return await self.search_database(
                        arguments.get("query", ""),
                        arguments.get("max_results", 5)
                    )
                elif name == "get_stats":
                    return await self.get_stats()
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool error: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def search_database(self, query: str, max_results: int = 5) -> list[types.TextContent]:
        try:
            logger.info(f"Remote search: '{query}'")
            
            # Connect to remote database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Simple search
            words = [w.strip().lower() for w in query.split() if len(w.strip()) > 2]
            if not words:
                return [types.TextContent(type="text", text="Please provide a valid query.")]
            
            conditions = []
            params = []
            for word in words:
                conditions.append("LOWER(content) LIKE %s")
                params.append(f"%{word}%")
            
            where_clause = " OR ".join(conditions)
            sql = f"SELECT content FROM documents WHERE {where_clause} LIMIT %s"
            params.append(max_results)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return [types.TextContent(type="text", text=f"No results found for: {query}")]
            
            results_text = f"Found {len(rows)} results for '{query}':\n\n"
            for i, (content,) in enumerate(rows, 1):
                results_text += f"{i}. {str(content)[:300]}...\n\n"
            
            return [types.TextContent(type="text", text=results_text)]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return [types.TextContent(type="text", text=f"Search failed: {str(e)}")]

    async def get_stats(self) -> list[types.TextContent]:
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            conn.close()
            
            return [types.TextContent(
                type="text", 
                text=f"Database contains {count} documents"
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Stats error: {str(e)}")]

    async def run(self):
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="remote-database-search",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

if __name__ == "__main__":
    server = RemoteDatabaseMCPServer()
    asyncio.run(server.run())
