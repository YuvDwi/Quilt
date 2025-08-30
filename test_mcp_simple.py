#!/usr/bin/env python3
"""
Test the simple MCP server
"""

import subprocess
import json
import time
import sys

def test_mcp_server():
    print("🧪 Testing Simple MCP Server...")
    
    try:
        # Start the MCP server
        process = subprocess.Popen(
            [sys.executable, "simple_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Send initialization
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_msg) + "\n")
        process.stdin.flush()
        
        # Wait and check if process is still running
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Server started successfully")
            
            # Send tools list request
            tools_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            process.stdin.write(json.dumps(tools_msg) + "\n")
            process.stdin.flush()
            time.sleep(1)
            
            print("✅ Tools request sent")
            
            # Test search
            search_msg = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_database",
                    "arguments": {"query": "machine learning"}
                }
            }
            
            process.stdin.write(json.dumps(search_msg) + "\n")
            process.stdin.flush()
            time.sleep(2)
            
            print("✅ Search request sent")
            print("✅ MCP server is working!")
            
        else:
            print("❌ Server failed to start")
            stderr = process.stderr.read()
            if stderr:
                print(f"Error: {stderr}")
        
        # Clean up
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_mcp_server()
    print("\n🔧 NEXT STEPS:")
    print("1. Restart Claude Desktop completely")
    print("2. Open new conversation")
    print("3. Ask: 'Search my database for machine learning'")
    print("4. Claude should now be able to search your database!")
