"""
Test script for the ChatGPT plugin

This script tests all the plugin endpoints and simulates how ChatGPT
would interact with your search database.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_plugin_manifest():
    """Test the plugin manifest endpoint"""
    print("🧪 Testing plugin manifest...")
    try:
        response = requests.get(f"{BASE_URL}/.well-known/ai-plugin.json")
        if response.status_code == 200:
            manifest = response.json()
            print("✅ Plugin manifest loaded successfully")
            print(f"   Plugin name: {manifest.get('name_for_human')}")
            print(f"   Description: {manifest.get('description_for_human')}")
            return True
        else:
            print(f"❌ Manifest request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Manifest test failed: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n🩺 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ Health check passed")
            print(f"   Status: {health.get('status')}")
            print(f"   Database connected: {health.get('database_connected')}")
            print(f"   Total documents: {health.get('total_documents')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health test failed: {e}")
        return False

def test_stats_endpoint():
    """Test the stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats endpoint working")
            db_info = stats.get('database_info', {})
            print(f"   Total documents: {db_info.get('total_documents')}")
            print(f"   Documents with embeddings: {db_info.get('documents_with_embeddings')}")
            print(f"   Database type: {db_info.get('database_type')}")
            print(f"   Embedding model: {db_info.get('embedding_model')}")
            return True
        else:
            print(f"❌ Stats request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats test failed: {e}")
        return False

def test_search_endpoint():
    """Test the search functionality"""
    print("\n🔍 Testing search endpoint...")
    
    test_queries = [
        {"query": "test", "search_type": "hybrid"},
        {"query": "example content", "search_type": "keyword"},
        {"query": "machine learning", "search_type": "vector"}
    ]
    
    for test_query in test_queries:
        try:
            print(f"\n   Testing: '{test_query['query']}' ({test_query['search_type']})")
            
            params = {
                "query": test_query["query"],
                "search_type": test_query["search_type"],
                "max_results": 3
            }
            
            response = requests.get(f"{BASE_URL}/search", params=params)
            
            if response.status_code == 200:
                results = response.json()
                print(f"   ✅ Found {results.get('total_results', 0)} results")
                
                for i, result in enumerate(results.get('results', [])[:2]):
                    content = result.get('content', '')
                    score = result.get('score', 0)
                    print(f"      {i+1}. Score: {score:.3f} - {content[:100]}...")
                    
            else:
                print(f"   ❌ Search failed: {response.status_code}")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Search test failed: {e}")

def test_openapi_schema():
    """Test the OpenAPI schema endpoint"""
    print("\n📝 Testing OpenAPI schema...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            print("✅ OpenAPI schema accessible")
            print(f"   Title: {schema.get('info', {}).get('title')}")
            print(f"   Endpoints: {', '.join(schema.get('paths', {}).keys())}")
            return True
        else:
            print(f"❌ OpenAPI schema failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenAPI test failed: {e}")
        return False

def simulate_chatgpt_interaction():
    """Simulate how ChatGPT would interact with the plugin"""
    print("\n🤖 Simulating ChatGPT interaction...")
    
    # This simulates what ChatGPT would do:
    # 1. Load the plugin manifest
    # 2. Check available endpoints
    # 3. Perform a search based on user query
    # 4. Use the results to formulate an answer
    
    user_question = "What information do you have about machine learning?"
    
    print(f"   User asks: '{user_question}'")
    print("   ChatGPT would:")
    print("   1. Recognize this needs a database search")
    print("   2. Call the search endpoint")
    
    try:
        # Simulate ChatGPT calling the search endpoint
        search_response = requests.get(f"{BASE_URL}/search", params={
            "query": "machine learning",
            "search_type": "hybrid",
            "max_results": 3
        })
        
        if search_response.status_code == 200:
            results = search_response.json()
            print(f"   3. Receive {results.get('total_results', 0)} relevant documents")
            print("   4. Use this information to craft a comprehensive answer")
            
            if results.get('results'):
                print("\n   📄 Retrieved content that ChatGPT would use:")
                for i, result in enumerate(results['results'][:2], 1):
                    content = result.get('content', '')
                    print(f"      Source {i}: {content[:150]}...")
                    
                print("\n   💡 ChatGPT would then say something like:")
                print("   'Based on the information in your database, here's what I found about machine learning...'")
                print("   [ChatGPT would then synthesize the retrieved content into a coherent answer]")
            else:
                print("   💭 No relevant content found - ChatGPT would mention this")
                
        else:
            print(f"   ❌ Search failed: {search_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Simulation failed: {e}")

def main():
    """Run all plugin tests"""
    print("🧪 ChatGPT Plugin Test Suite")
    print("="*50)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print("❌ Plugin server not running!")
        print("Please start it with: python3 chatgpt_plugin_api.py")
        return False
    
    # Run all tests
    tests = [
        test_plugin_manifest,
        test_health_endpoint,
        test_stats_endpoint,
        test_openapi_schema,
        test_search_endpoint,
        simulate_chatgpt_interaction
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "="*50)
    print(f"🎯 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your plugin is ready for ChatGPT.")
        print("\nNext steps:")
        print("1. Keep the server running: python3 chatgpt_plugin_api.py")
        print("2. Follow the setup instructions in plugin_setup.py")
        print("3. Add the plugin to ChatGPT using the manifest URL:")
        print(f"   {BASE_URL}/.well-known/ai-plugin.json")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    main()
