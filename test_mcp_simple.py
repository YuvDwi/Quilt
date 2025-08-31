#!/usr/bin/env python3
"""
Very simple MCP test - minimal implementation
"""

import asyncio
import sys
import json
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

# Create server
server = Server("test")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    return ListToolsResult(
        tools=[
            Tool(
                name="hello",
                description="Say hello",
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
    if name == "hello":
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text="Hello! MCP is working! Your quilt-test has 2 documents at https://quilt-vkfk.onrender.com"
            )]
        )
    
    return CallToolResult(
        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
    )

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="test",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())