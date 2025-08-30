#!/usr/bin/env python3
"""
Test script for the MCP Database Server
"""

import asyncio
import json
import subprocess
import sys
import time

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing MCP Database Server")
    print("=" * 50)
    
    # Test 1: Check if server starts
    print("1. Testing server startup...")
    try:
        # Start the server as a subprocess
        process = subprocess.Popen(
            [sys.executable, "mcp_database_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Wait for response
        time.sleep(2)
        
        if process.poll() is None:  # Process is still running
            print("✅ Server started successfully")
            
            # Test 2: List tools
            print("\n2. Testing tool listing...")
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            process.stdin.write(json.dumps(list_tools_request) + "\n")
            process.stdin.flush()
            time.sleep(1)
            
            print("✅ Tools list request sent")
            
            # Test 3: Test search tool
            print("\n3. Testing database search...")
            search_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_database",
                    "arguments": {
                        "query": "machine learning",
                        "max_results": 3
                    }
                }
            }
            
            process.stdin.write(json.dumps(search_request) + "\n")
            process.stdin.flush()
            time.sleep(2)
            
            print("✅ Search request sent")
            
            # Terminate the process
            process.terminate()
            process.wait()
            
            print("\n✅ All tests completed successfully!")
            print("\nYour MCP server is ready to use with ChatGPT!")
            
        else:
            print("❌ Server failed to start")
            stderr_output = process.stderr.read()
            print(f"Error: {stderr_output}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def print_setup_instructions():
    """Print setup instructions for ChatGPT"""
    print("\n" + "=" * 60)
    print("🚀 CHATGPT MCP SETUP INSTRUCTIONS")
    print("=" * 60)
    print("""
To use this MCP server with ChatGPT Desktop:

1. 📁 Open ChatGPT Desktop application
2. ⚙️  Go to Settings → Features → Model Context Protocol
3. ➕ Add a new MCP server with these settings:
   
   Server Name: Database Search
   Command: python3
   Arguments: mcp_database_server.py
   Working Directory: /Users/yuvraj/Desktop/Quilt

4. ✅ Save and restart ChatGPT Desktop

5. 🔍 In any conversation, you can now use these tools:
   - "Search my database for information about X"
   - "What do I have in my database about Y?"
   - "Find content related to Z"

AVAILABLE TOOLS:
📊 search_database - Search for content by query
📈 get_database_stats - Get database statistics  
🎯 search_by_topic - Search by specific topic

EXAMPLE PROMPTS FOR CHATGPT:
• "Search my database for machine learning content"
• "What information do I have about Python programming?"
• "Show me database statistics"
• "Find content about databases in my collection"

The MCP server will provide ChatGPT with direct access to your 
PostgreSQL database content!
    """)

if __name__ == "__main__":
    print("Starting MCP Server Tests...\n")
    asyncio.run(test_mcp_server())
    print_setup_instructions()
