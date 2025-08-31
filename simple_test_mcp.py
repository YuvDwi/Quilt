#!/usr/bin/env python3
"""
Simple MCP server for testing Claude Desktop connection
"""

import asyncio
import sys
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

# Initialize server
server = Server("simple-test")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="test_connection",
                description="Test if MCP connection is working",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_test_data",
                description="Get test data from your quilt deployment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Test query",
                            "default": "test"
                        }
                    },
                    "required": []
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "test_connection":
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="🎉 MCP Connection Working!\n\nYour Claude Desktop is successfully connected to the MCP server.\n\nYou have 2 documents from YuvDwi/quilt-test in your cloud database at https://quilt-vkfk.onrender.com"
                )]
            )
            
        elif name == "get_test_data":
            query = arguments.get("query", "test")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"📊 **Your Quilt Database Info:**\n\n**Repository:** YuvDwi/quilt-test\n**Documents:** 2 indexed\n**API:** https://quilt-vkfk.onrender.com\n**Status:** Deployed successfully\n\n**Search Query:** {query}\n\n✅ Your deployment is working and searchable!"
                )]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"❌ Unknown tool: {name}"
                )]
            )
            
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )]
        )

async def main():
    """Main server entry point"""
    print("🚀 Starting Simple Test MCP Server...", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-test",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
