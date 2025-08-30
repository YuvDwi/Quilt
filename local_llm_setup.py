#!/usr/bin/env python3
"""
Local LLM Setup with Database Integration
Works with Ollama, LM Studio, and other local models
"""

import requests
import json
import psycopg2
from typing import List, Dict

class LocalLLMDatabaseChat:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.db_config = {
            "host": "localhost",
            "port": "5432",
            "database": "quilt_embeddings",
            "user": "quilt_user",
            "password": "your_secure_password"
        }
    
    def search_database(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search your database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            words = [w.strip().lower() for w in query.split() if len(w.strip()) > 2]
            if not words:
                return []
            
            conditions = []
            params = []
            for word in words:
                conditions.append("LOWER(content) LIKE %s")
                params.append(f"%{word}%")
            
            where_clause = " OR ".join(conditions)
            sql = f"SELECT content FROM documents WHERE {where_clause} LIMIT %s"
            params.append(max_results)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [{"content": str(row[0])} for row in rows]
            
        except Exception as e:
            print(f"Database error: {e}")
            return []
    
    def chat_with_context(self, user_question: str, model="llama3.2"):
        """Chat with LLM using database context"""
        
        # 1. Search database for relevant context
        print(f"🔍 Searching database for: '{user_question}'")
        search_results = self.search_database(user_question)
        
        # 2. Build context
        context = ""
        if search_results:
            context = "Based on this information from the database:\n\n"
            for i, result in enumerate(search_results, 1):
                context += f"{i}. {result['content'][:400]}...\n\n"
            context += f"Please answer this question: {user_question}"
        else:
            context = f"No relevant information found in the database. Please answer this question based on your general knowledge: {user_question}"
        
        # 3. Send to local LLM
        print(f"🤖 Asking {model}...")
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": context,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                ai_response = response.json()["response"]
                return {
                    "answer": ai_response,
                    "sources_found": len(search_results),
                    "model": model
                }
            else:
                return {"error": f"LLM API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Failed to connect to local LLM: {e}"}

def main():
    """Interactive chat with database context"""
    chat = LocalLLMDatabaseChat()
    
    print("🚀 LOCAL LLM + DATABASE CHAT")
    print("=" * 50)
    print("Ask questions and I'll search your database for context!")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        print()
        result = chat.chat_with_context(user_input)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"🤖 AI Response ({result['model']}):")
            print(f"📊 Found {result['sources_found']} relevant sources")
            print()
            print(result['answer'])
        
        print("\n" + "-" * 50 + "\n")

if __name__ == "__main__":
    print("Setting up local LLM with database integration...")
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama running with {len(models)} models")
            for model in models:
                print(f"   - {model['name']}")
        else:
            print("❌ Ollama not responding")
    except:
        print("❌ Ollama not running. Install with: brew install ollama")
        print("   Then run: ollama serve")
        print("   And: ollama pull llama3.2")
    
    print()
    main()
