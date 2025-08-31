#!/usr/bin/env python3
"""
Updated Cloud MCP Server for Quilt - Uses the general search API
"""

import asyncio
import json
import os
import sys
import requests
from typing import Any, Dict, List
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# Cloud API Configuration
CLOUD_API_URL = os.getenv('CLOUD_API_URL', 'https://quilt-vkfk.onrender.com')

class QuiltMCPServer:
    def __init__(self):
        self.api_url = CLOUD_API_URL
        print(f"🌐 Quilt MCP Server initialized", file=sys.stderr)
        print(f"🔗 API URL: {self.api_url}", file=sys.stderr)

    async def search_content(self, query: str, search_type: str = "hybrid", limit: int = 5) -> TextContent:
        """Search all deployed content using the general search API"""
        try:
            response = requests.get(
                f"{self.api_url}/search",
                params={
                    "query": query,
                    "search_type": search_type,
                    "limit": limit
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('results'):
                    results_text = f"🔍 **Search Results for '{query}'**\n"
                    results_text += f"Found {data['total_results']} results using {search_type} search:\n\n"
                    
                    for i, result in enumerate(data['results'], 1):
                        metadata = result.get('metadata', {})
                        file_name = metadata.get('file_name', 'Unknown file')
                        repo_name = metadata.get('repo_name', 'Unknown repo')
                        llm_type = metadata.get('llm_type', 'content')
                        element_tag = metadata.get('element_tag', 'div')
                        score = result.get('score', 0)
                        
                        results_text += f"**{i}. {llm_type.title()} from {repo_name}**\n"
                        results_text += f"📁 File: {file_name}\n"
                        results_text += f"🏷️ Element: <{element_tag} data-llm=\"{llm_type}\">\n"
                        results_text += f"📊 Relevance Score: {score:.2f}\n"
                        results_text += f"📄 Content:\n{result['content']}\n\n"
                        results_text += "---\n\n"
                    
                    return TextContent(text=results_text)
                else:
                    return TextContent(text=f"❌ No results found for '{query}'.\n\nTry:\n- Different keywords\n- Check if content has been deployed\n- Use broader search terms")
            else:
                return TextContent(text=f"❌ Search API error: HTTP {response.status_code}")
                
        except Exception as e:
            return TextContent(text=f"❌ Search failed: {str(e)}")

    async def search_user_content(self, user_id: str, query: str, search_type: str = "hybrid", limit: int = 5) -> TextContent:
        """Search specific user's deployed content"""
        try:
            response = requests.get(
                f"{self.api_url}/search/{user_id}",
                params={
                    "query": query,
                    "search_type": search_type,
                    "limit": limit
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('results'):
                    results_text = f"🔍 **{user_id}'s Content Search Results for '{query}'**\n"
                    results_text += f"Found {data['total_results']} results:\n\n"
                    
                    for i, result in enumerate(data['results'], 1):
                        metadata = result.get('metadata', {})
                        file_name = metadata.get('file_name', 'Unknown file')
                        repo_name = metadata.get('repo_name', 'Unknown repo')
                        llm_type = metadata.get('llm_type', 'content')
                        score = result.get('score', 0)
                        
                        results_text += f"**{i}. {llm_type.title()}** (Score: {score:.2f})\n"
                        results_text += f"📁 {repo_name} → {file_name}\n"
                        results_text += f"📄 {result['content']}\n\n"
                        results_text += "---\n\n"
                    
                    return TextContent(text=results_text)
                else:
                    return TextContent(text=f"❌ No results found for user '{user_id}' with query '{query}'.")
            else:
                return TextContent(text=f"❌ User search API error: HTTP {response.status_code}")
                
        except Exception as e:
            return TextContent(text=f"❌ User search failed: {str(e)}")

    async def get_database_stats(self) -> TextContent:
        """Get database statistics and health info"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                
                stats_text = "📊 **Quilt Database Statistics**\n\n"
                stats_text += f"🗄️ Total Documents: {stats.get('total_documents', 'Unknown')}\n"
                stats_text += f"🚀 Total Deployments: {stats.get('total_deployments', 'Unknown')}\n\n"
                
                if 'recent_deployments' in stats:
                    stats_text += "📈 **Recent Deployments:**\n"
                    for deployment in stats['recent_deployments']:
                        stats_text += f"• {deployment.get('repo_name', 'Unknown')} - {deployment.get('sections_indexed', 0)} sections\n"
                
                return TextContent(text=stats_text)
            else:
                return TextContent(text=f"❌ Stats API error: HTTP {response.status_code}")
                
        except Exception as e:
            return TextContent(text=f"❌ Failed to get stats: {str(e)}")

# Initialize the MCP server
quilt_server = QuiltMCPServer()
server = Server("quilt-search")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="search_content",
                description="Search through all deployed content using vector, keyword, or hybrid search",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "search_type": {
                            "type": "string",
                            "enum": ["vector", "keyword", "hybrid"],
                            "description": "Type of search to perform",
                            "default": "hybrid"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="search_user_content",
                description="Search through a specific user's deployed content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to search within"
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "search_type": {
                            "type": "string",
                            "enum": ["vector", "keyword", "hybrid"],
                            "description": "Type of search to perform",
                            "default": "hybrid"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        }
                    },
                    "required": ["user_id", "query"]
                }
            ),
            Tool(
                name="get_database_stats",
                description="Get database statistics and deployment information",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls"""
    try:
        if request.name == "search_content":
            query = request.arguments.get("query", "")
            search_type = request.arguments.get("search_type", "hybrid")
            limit = request.arguments.get("limit", 5)
            
            result = await quilt_server.search_content(query, search_type, limit)
            return CallToolResult(content=[result])
            
        elif request.name == "search_user_content":
            user_id = request.arguments.get("user_id", "")
            query = request.arguments.get("query", "")
            search_type = request.arguments.get("search_type", "hybrid")
            limit = request.arguments.get("limit", 5)
            
            result = await quilt_server.search_user_content(user_id, query, search_type, limit)
            return CallToolResult(content=[result])
            
        elif request.name == "get_database_stats":
            result = await quilt_server.get_database_stats()
            return CallToolResult(content=[result])
            
        else:
            return CallToolResult(
                content=[TextContent(text=f"Unknown tool: {request.name}")],
                isError=True
            )
            
    except Exception as e:
        return CallToolResult(
            content=[TextContent(text=f"Tool execution failed: {str(e)}")],
            isError=True
        )

async def main():
    """Main entry point"""
    print("🚀 Starting Quilt MCP Server...", file=sys.stderr)
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="quilt-search",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
