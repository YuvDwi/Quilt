#!/usr/bin/env python3
"""
Test if Claude Desktop can see MCP tools
"""

import subprocess
import json
import sys

def test_mcp_connection():
    """Test MCP server connection"""
    
    print("🧪 TESTING CLAUDE DESKTOP MCP CONNECTION")
    print("=" * 50)
    
    # Check if MCP server can start
    print("1. Testing MCP server startup...")
    
    try:
        # Test the cloud API directly
        import requests
        response = requests.get("https://quilt-vkfk.onrender.com/stats", timeout=10)
        print(f"   ✅ Cloud API accessible: {response.status_code}")
        stats = response.json()
        print(f"   📊 Database has {stats['total_documents']} documents")
    except Exception as e:
        print(f"   ❌ Cloud API error: {e}")
        return
    
    # Check MCP dependencies
    print("\n2. Checking MCP dependencies...")
    try:
        import mcp
        print("   ✅ MCP library installed")
    except ImportError:
        print("   ❌ MCP library missing - install with: pip install mcp")
        return
    
    # Check config file
    print("\n3. Checking Claude Desktop config...")
    config_path = "/Users/yuvraj/Library/Application Support/Claude/claude_desktop_config.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'mcpServers' in config and 'database-search' in config['mcpServers']:
            print("   ✅ MCP server configured in Claude Desktop")
            server_config = config['mcpServers']['database-search']
            print(f"   📁 Command: {server_config['command']}")
            print(f"   📄 Script: {server_config['args'][0]}")
            print(f"   🌐 API URL: {server_config['env']['CLOUD_API_URL']}")
        else:
            print("   ❌ MCP server not found in config")
            
    except Exception as e:
        print(f"   ❌ Config error: {e}")
    
    print("\n4. Next steps:")
    print("   1. Completely quit Claude Desktop")
    print("   2. Reopen Claude Desktop")
    print("   3. Wait 10-15 seconds for MCP to connect")
    print("   4. Try: 'What tools do you have available?'")
    print("   5. Then try: 'Search my database for quilt-test'")
    
    print(f"\n🎯 If Claude still doesn't see the tools:")
    print("   - Check Claude Desktop logs (if available)")
    print("   - Try restarting your computer")
    print("   - Verify Python path: /usr/local/bin/python3")

if __name__ == "__main__":
    test_mcp_connection()
