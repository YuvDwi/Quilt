"""
Setup script for ChatGPT Plugin deployment

This script helps you set up and test your ChatGPT plugin locally
and provides instructions for deployment.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_database_connection():
    """Test if the database is accessible"""
    print("🔍 Testing database connection...")
    try:
        from postgres_hybrid_search import PostgresHybridVectorSearch
        search_engine = PostgresHybridVectorSearch()
        stats = search_engine.get_stats()
        print(f"✅ Database connected: {stats['total_documents']} documents indexed")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_plugin_endpoints():
    """Test the plugin endpoints"""
    print("\n🌐 Testing plugin endpoints...")
    try:
        import requests
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
        
        # Test manifest endpoint
        response = requests.get(f"{base_url}/.well-known/ai-plugin.json")
        if response.status_code == 200:
            print("✅ Plugin manifest accessible")
        else:
            print(f"❌ Plugin manifest failed: {response.status_code}")
        
        # Test search endpoint
        response = requests.get(f"{base_url}/search?query=test")
        if response.status_code == 200:
            print("✅ Search endpoint working")
            return True
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Plugin server not running")
        return False
    except Exception as e:
        print(f"❌ Plugin test failed: {e}")
        return False

def start_plugin_server():
    """Start the plugin server"""
    print("\n🚀 Starting ChatGPT plugin server...")
    try:
        # Check if server is already running
        import requests
        try:
            requests.get("http://localhost:8000/health", timeout=2)
            print("ℹ️ Server already running on http://localhost:8000")
            return True
        except:
            pass
        
        # Start the server
        cmd = [sys.executable, "chatgpt_plugin_api.py"]
        print(f"Running: {' '.join(cmd)}")
        subprocess.Popen(cmd)
        print("✅ Plugin server starting on http://localhost:8000")
        print("📋 Plugin manifest: http://localhost:8000/.well-known/ai-plugin.json")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def create_env_for_plugin():
    """Create or update environment variables for plugin"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            content = f.read()
        
        # Add plugin URL if not present
        if "PLUGIN_URL" not in content:
            with open(env_file, "a") as f:
                f.write("\n# ChatGPT Plugin Configuration\n")
                f.write("PLUGIN_URL=http://localhost:8000\n")
            print("✅ Added PLUGIN_URL to .env file")
        else:
            print("ℹ️ PLUGIN_URL already configured")
    else:
        print("⚠️ No .env file found. Please create one based on env.example")

def show_chatgpt_instructions():
    """Show instructions for using with ChatGPT"""
    print("\n" + "="*60)
    print("🤖 ChatGPT Plugin Setup Instructions")
    print("="*60)
    print()
    print("1. Start the plugin server:")
    print("   python3 chatgpt_plugin_api.py")
    print()
    print("2. Your plugin will be available at:")
    print("   http://localhost:8000")
    print()
    print("3. Plugin manifest URL:")
    print("   http://localhost:8000/.well-known/ai-plugin.json")
    print()
    print("4. For ChatGPT Plus users:")
    print("   - Go to ChatGPT")
    print("   - Click on your profile → Settings → Beta Features")
    print("   - Enable 'Plugins'")
    print("   - In a new chat, select 'Plugins' from the model dropdown")
    print("   - Click 'Plugin store' → 'Develop your own plugin'")
    print("   - Enter: http://localhost:8000")
    print()
    print("5. Test the plugin by asking ChatGPT:")
    print("   'Search for information about [your topic]'")
    print()
    print("6. For production deployment:")
    print("   - Deploy to a public server (Railway, Heroku, etc.)")
    print("   - Update PLUGIN_URL in your environment")
    print("   - Ensure HTTPS is enabled")
    print("   - Submit to OpenAI plugin store (optional)")
    print()
    print("="*60)

def main():
    """Main setup function"""
    print("🎯 ChatGPT Plugin Setup for Quilt Database Search")
    print("="*60)
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database not ready. Please run:")
        print("   python3 test_postgres_setup.py")
        return False
    
    # Setup environment
    create_env_for_plugin()
    
    # Show instructions
    show_chatgpt_instructions()
    
    # Ask if user wants to start server
    try:
        response = input("\nStart the plugin server now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            start_plugin_server()
            print("\n⏳ Waiting a moment for server to start...")
            import time
            time.sleep(3)
            test_plugin_endpoints()
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")
    
    return True

if __name__ == "__main__":
    main()
