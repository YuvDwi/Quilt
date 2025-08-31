#!/usr/bin/env python3
"""
Debug MCP connection issues
"""

import subprocess
import os
import sys
import json

def debug_mcp_connection():
    """Debug MCP server connection"""
    
    print("🔍 DEBUGGING MCP CONNECTION ISSUES")
    print("=" * 50)
    
    # Check if the MCP server script is executable
    script_path = "/Users/yuvraj/Desktop/Quilt/cloud_mcp_server.py"
    
    print("1. Checking file permissions...")
    if os.path.exists(script_path):
        print(f"   ✅ Script exists: {script_path}")
        if os.access(script_path, os.X_OK):
            print("   ✅ Script is executable")
        else:
            print("   ⚠️  Script not executable - fixing...")
            os.chmod(script_path, 0o755)
            print("   ✅ Made script executable")
    else:
        print(f"   ❌ Script not found: {script_path}")
        return
    
    # Check Python path
    print("\n2. Checking Python path...")
    python_path = "/usr/local/bin/python3"
    if os.path.exists(python_path):
        print(f"   ✅ Python exists: {python_path}")
    else:
        print(f"   ❌ Python not found: {python_path}")
        # Try to find Python
        result = subprocess.run(["which", "python3"], capture_output=True, text=True)
        if result.returncode == 0:
            actual_python = result.stdout.strip()
            print(f"   💡 Found Python at: {actual_python}")
            print(f"   🔧 Update config to use: {actual_python}")
        return
    
    # Test MCP server directly
    print("\n3. Testing MCP server startup...")
    try:
        # Test if we can import required modules
        test_cmd = [python_path, "-c", "import mcp, requests, asyncio; print('All imports OK')"]
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ All Python dependencies available")
        else:
            print(f"   ❌ Import error: {result.stderr}")
            return
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return
    
    # Check environment variables
    print("\n4. Checking environment...")
    api_url = "https://quilt-vkfk.onrender.com"
    try:
        import requests
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ API accessible: {api_url}")
        else:
            print(f"   ⚠️  API returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API error: {e}")
    
    print("\n5. Suggested fixes:")
    print("   A. Try restarting Claude Desktop completely")
    print("   B. Check Claude Desktop logs (if available)")
    print("   C. Try a simpler MCP server first")
    print("   D. Verify the config file syntax")
    
    # Show current config
    print("\n6. Current Claude Desktop config:")
    config_path = "/Users/yuvraj/Library/Application Support/Claude/claude_desktop_config.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(json.dumps(config, indent=2))
    except Exception as e:
        print(f"   ❌ Config error: {e}")

if __name__ == "__main__":
    debug_mcp_connection()
