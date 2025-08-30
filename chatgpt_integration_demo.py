"""
Demo: How to integrate your search with ChatGPT-like interactions
"""

import requests
import json

def search_database(query):
    """Search your database"""
    try:
        response = requests.get(f"http://localhost:9000/search?query={query}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def ai_assistant_with_search(user_question):
    """Simulate how ChatGPT would use your database"""
    
    print(f"🤖 User asks: '{user_question}'")
    print("🔍 Searching database for relevant information...")
    
    # Search your database
    search_results = search_database(user_question)
    
    if search_results.get("found", 0) > 0:
        print(f"✅ Found {search_results['found']} relevant results:")
        
        # Show what information was found
        context = []
        for result in search_results["results"][:3]:  # Top 3 results
            print(f"   📄 {result['content'][:100]}...")
            context.append(result["content"])
        
        # This is the information ChatGPT would use
        print("\n💡 ChatGPT would now use this information to answer:")
        print(f"Based on your database, here's what I found about '{user_question}':")
        
        for i, result in enumerate(search_results["results"][:2], 1):
            print(f"\n{i}. {result['content']}")
            if result['metadata']:
                print(f"   Source: {result['metadata']}")
    
    else:
        print("❌ No relevant information found in database")
    
    return search_results

# Test examples
if __name__ == "__main__":
    examples = [
        "What is machine learning?",
        "How does Python programming work?", 
        "Tell me about databases"
    ]
    
    for example in examples:
        ai_assistant_with_search(example)
        print("\n" + "="*80 + "\n")
