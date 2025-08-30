#!/usr/bin/env python3
"""
Debug MCP Server - with error logging to stderr
"""

import asyncio
import json
import sys
import traceback
import psycopg2
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent
import mcp.types as types

def debug_log(message):
    """Log debug messages to stderr so Claude Desktop can see them"""
    print(f"DEBUG: {message}", file=sys.stderr, flush=True)

# Create server instance
server = Server("debug-database-search")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    debug_log("list_tools called")
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
    debug_log(f"call_tool called: {name} with {arguments}")
    try:
        if name == "search_database":
            query = arguments.get("query", "")
            return await search_database(query)
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        debug_log(f"Error in call_tool: {e}")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def search_database(query: str) -> list[types.TextContent]:
    """Search the database"""
    debug_log(f"search_database called with query: {query}")
    try:
        # Test database connection
        debug_log("Attempting database connection...")
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="quilt_embeddings",
            user="quilt_user",
            password="your_secure_password"
        )
        debug_log("Database connected successfully")
        
        cursor = conn.cursor()
        
        # Simple test query first
        debug_log("Testing simple query...")
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        debug_log(f"Found {count} documents in database")
        
        # Simple search
        words = [w.strip().lower() for w in query.split() if len(w.strip()) > 2]
        if not words:
            conn.close()
            return [types.TextContent(type="text", text="Please provide a valid search query.")]
        
        debug_log(f"Search words: {words}")
        
        # Build query
        conditions = []
        params = []
        for word in words:
            conditions.append("LOWER(content) LIKE %s")
            params.append(f"%{word}%")
        
        where_clause = " OR ".join(conditions)
        sql = f"SELECT content FROM documents WHERE {where_clause} LIMIT 3"
        
        debug_log(f"Executing SQL: {sql}")
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        debug_log(f"Query returned {len(rows)} rows")
        
        if not rows:
            return [types.TextContent(
                type="text", 
                text=f"No results found for query: '{query}'"
            )]
        
        # Format results
        result_text = f"Found {len(rows)} results for '{query}':\n\n"
        for i, (content,) in enumerate(rows, 1):
            result_text += f"{i}. {str(content)[:200]}...\n\n"
        
        debug_log("Returning search results")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        debug_log(f"Database search error: {e}")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return [types.TextContent(
            type="text", 
            text=f"Database search error: {str(e)}"
        )]

async def main():
    debug_log("Starting debug MCP server...")
    try:
        # Run the server
        from mcp.server.stdio import stdio_server
        
        debug_log("Creating stdio server...")
        async with stdio_server() as (read_stream, write_stream):
            debug_log("Running MCP server...")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="debug-database-search",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        debug_log(f"Server error: {e}")
        debug_log(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    debug_log("Script starting...")
    try:
        asyncio.run(main())
    except Exception as e:
        debug_log(f"Main error: {e}")
        debug_log(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
