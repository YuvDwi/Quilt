#!/usr/bin/env python3
"""
Simple MCP Server for Database Search - Claude Desktop Compatible
"""

import asyncio
import json
import psycopg2
import sys
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent
import mcp.types as types

# Create server instance
server = Server("simple-database-search")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_database",
            description="Search the PostgreSQL database for relevant content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    if name == "search_database":
        query = arguments.get("query", "")
        return await search_database(query)
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def search_database(query: str) -> list[types.TextContent]:
    """Search the database"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="quilt_embeddings",
            user="quilt_user",
            password="your_secure_password"
        )
        cursor = conn.cursor()
        
        # Simple search
        words = [w.strip().lower() for w in query.split() if len(w.strip()) > 2]
        if not words:
            return [types.TextContent(type="text", text="Please provide a valid search query.")]
        
        # Build query
        conditions = []
        params = []
        for word in words:
            conditions.append("LOWER(content) LIKE %s")
            params.append(f"%{word}%")
        
        where_clause = " OR ".join(conditions)
        sql = f"SELECT content FROM documents WHERE {where_clause} LIMIT 3"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return [types.TextContent(
                type="text", 
                text=f"No results found for query: '{query}'"
            )]
        
        # Format results
        result_text = f"Found {len(rows)} results for '{query}':\n\n"
        for i, (content,) in enumerate(rows, 1):
            result_text += f"{i}. {str(content)[:200]}...\n\n"
        
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        return [types.TextContent(
            type="text", 
            text=f"Database search error: {str(e)}"
        )]

async def main():
    # Run the server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-database-search",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
