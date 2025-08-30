#!/usr/bin/env python3
"""
Cloud MCP Server for Quilt - Connects to Render-hosted API
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
CLOUD_API_URL = os.getenv('CLOUD_API_URL', 'https://quilt-api-xyz.onrender.com')

class CloudQuiltMCPServer:
    def __init__(self):
        self.api_url = CLOUD_API_URL
        print(f"🌐 Cloud MCP Server initialized", file=sys.stderr)
        print(f"🔗 API URL: {self.api_url}", file=sys.stderr)

    def search_cloud_database(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search the cloud-hosted database via API"""
        try:
            # For now, use stats endpoint to get database info
            # In a full implementation, you'd add a search endpoint to the cloud API
            response = requests.get(f"{self.api_url}/stats", timeout=30)
            response.raise_for_status()
            
            stats = response.json()
            
            # Simple keyword matching for demo
            # In production, you'd implement proper search in the cloud API
            results = []
            if 'repositories' in stats:
                for repo, count in stats['repositories'].items():
                    if any(keyword.lower() in repo.lower() for keyword in query.split()):
                        results.append({
                            'repo_name': repo,
                            'document_count': count,
                            'relevance': 'keyword_match'
                        })
            
            return {
                'query': query,
                'total_results': len(results),
                'results': results[:limit],
                'database_stats': stats
            }
            
        except Exception as e:
            print(f"❌ Cloud search error: {e}", file=sys.stderr)
            return {
                'query': query,
                'error': str(e),
                'total_results': 0,
                'results': []
            }

    def get_cloud_database_stats(self) -> Dict[str, Any]:
        """Get statistics from cloud database"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Cloud stats error: {e}", file=sys.stderr)
            return {'error': str(e), 'total_documents': 0}

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status from cloud API"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Cloud health error: {e}", file=sys.stderr)
            return {'status': 'error', 'error': str(e)}

# Initialize server
server = Server("cloud-quilt-database")
quilt_server = CloudQuiltMCPServer()

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools for Claude Desktop"""
    return ListToolsResult(
        tools=[
            Tool(
                name="search_cloud_database",
                description="Search the cloud-hosted Quilt database for relevant content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query to find relevant documents"
                        },
                        "limit": {
                            "type": "integer", 
                            "description": "Maximum number of results to return",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_cloud_database_stats",
                description="Get statistics about the cloud database contents",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_cloud_health",
                description="Check the health status of the cloud API and database",
                inputSchema={
                    "type": "object", 
                    "properties": {},
                    "required": []
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls from Claude Desktop"""
    try:
        if name == "search_cloud_database":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 10)
            
            print(f"🔍 Searching cloud database for: {query}", file=sys.stderr)
            result = quilt_server.search_cloud_database(query, limit)
            
            if result.get('error'):
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"❌ Search failed: {result['error']}"
                    )]
                )
            
            # Format results for Claude
            if result['total_results'] == 0:
                response_text = f"No results found for '{query}' in the cloud database."
            else:
                response_text = f"Found {result['total_results']} results for '{query}':\n\n"
                for i, item in enumerate(result['results'], 1):
                    response_text += f"{i}. **{item['repo_name']}**\n"
                    response_text += f"   - Documents: {item['document_count']}\n"
                    response_text += f"   - Match: {item['relevance']}\n\n"
            
            # Add database stats
            stats = result.get('database_stats', {})
            response_text += f"\n📊 **Database Overview:**\n"
            response_text += f"Total Documents: {stats.get('total_documents', 0)}\n"
            response_text += f"Repositories: {len(stats.get('repositories', {}))}\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
            
        elif name == "get_cloud_database_stats":
            print("📊 Getting cloud database stats", file=sys.stderr)
            stats = quilt_server.get_cloud_database_stats()
            
            if stats.get('error'):
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"❌ Failed to get stats: {stats['error']}"
                    )]
                )
            
            response_text = "📊 **Cloud Database Statistics:**\n\n"
            response_text += f"**Total Documents:** {stats.get('total_documents', 0)}\n\n"
            
            if 'repositories' in stats and stats['repositories']:
                response_text += "**Repositories:**\n"
                for repo, count in sorted(stats['repositories'].items(), key=lambda x: x[1], reverse=True):
                    response_text += f"- {repo}: {count} documents\n"
            else:
                response_text += "No repositories found.\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
            
        elif name == "get_cloud_health":
            print("🏥 Checking cloud health", file=sys.stderr)
            health = quilt_server.get_health_status()
            
            if health.get('error'):
                return CallToolResult(
                    content=[TextContent(
                        type="text", 
                        text=f"❌ Health check failed: {health['error']}"
                    )]
                )
            
            status = health.get('status', 'unknown')
            postgres = health.get('postgres', 'unknown')
            docs = health.get('documents_indexed', 0)
            
            response_text = f"🏥 **Cloud System Health:**\n\n"
            response_text += f"**Status:** {status}\n"
            response_text += f"**Database:** {postgres}\n" 
            response_text += f"**Documents Indexed:** {docs}\n"
            response_text += f"**API URL:** {quilt_server.api_url}\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"❌ Unknown tool: {name}"
                )]
            )
            
    except Exception as e:
        print(f"❌ Tool call error: {e}", file=sys.stderr)
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ Error executing {name}: {str(e)}"
            )]
        )

async def main():
    """Main server entry point"""
    print("🚀 Starting Cloud Quilt MCP Server...", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="cloud-quilt-database",
                server_version="2.0.0-cloud",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    print("🌐 Cloud MCP Server starting...", file=sys.stderr)
    asyncio.run(main())
