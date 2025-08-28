#!/usr/bin/env python3

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import json
import sqlite3
import re
from typing import List, Dict, Any, Optional

class EnhancedHTMLParser:
    def __init__(self):
        self.db_path = "search_data.db"
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content ON documents(content)")
    
    def add_document(self, content: str, metadata: Dict = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO documents (content, metadata) VALUES (?, ?)",
                (content, json.dumps(metadata) if metadata else None)
            )
    
    def parse_html_file(self, file_path: str) -> List[Dict[str, str]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        pairs = []
        
        title_elements = soup.find_all(attrs={"data-llm": "title"})
        
        for title_elem in title_elements:
            content_elem = self._find_next_content(title_elem)
            
            if content_elem:
                title_text = title_elem.get_text(strip=True)
                content_text = content_elem.get_text(strip=True)
                
                pairs.append({
                    'title': title_text,
                    'content': content_text
                })
                
                searchable_content = f"{title_text}\n\n{content_text}"
                
                metadata = {
                    'title': title_text,
                    'source_file': file_path,
                    'type': 'html_section',
                    'title_length': len(title_text),
                    'content_length': len(content_text)
                }
                
                self.add_document(searchable_content, metadata)
        
        return pairs
    
    def _find_next_content(self, title_element):
        parent = title_element.parent
        
        if parent:
            content_elements = parent.find_all(attrs={"data-llm": "content"})
            
            for content_elem in content_elements:
                if content_elem.find_previous_sibling() == title_element:
                    return content_elem
            
            if content_elements:
                return content_elements[0]
        
        next_elements = title_element.find_next_siblings()
        for elem in next_elements:
            if elem.get('data-llm') == 'content':
                return elem
        
        return None
    
    def search_similar(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        query_text = query_text.replace("\n", " ").strip()
        query_vector = self.model.encode(query_text)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT content, embedding, metadata FROM documents")
            results = []
            
            for row in cursor.fetchall():
                content, embedding_bytes, metadata = row
                stored_vector = np.frombuffer(embedding_bytes, dtype=np.float32)
                
                similarity = np.dot(query_vector, stored_vector)
                results.append({
                    'content': content,
                    'similarity_score': float(similarity),
                    'metadata': json.loads(metadata) if metadata else {}
                })
        
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:k]
    
    def hybrid_search(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        query_text = query_text.replace("\n", " ").strip().lower()
        keywords = re.findall(r'\b\w+\b', query_text)
        vector_results = self.search_similar(query_text, k=k*2)
        
        scored_results = []
        for result in vector_results:
            content_lower = result['content'].lower()
            
            keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
            keyword_score = keyword_matches / len(keywords) if keywords else 0
            
            phrase_bonus = 0.3 if query_text in content_lower else 0
            
            order_bonus = 0
            if len(keywords) > 1:
                for i in range(len(keywords) - 1):
                    if keywords[i] + " " + keywords[i + 1] in content_lower:
                        order_bonus += 0.1
            
            hybrid_score = (result['similarity_score'] * 0.6 + 
                           keyword_score * 0.3 + 
                           phrase_bonus + 
                           order_bonus)
            
            scored_results.append({
                **result,
                'keyword_score': keyword_score,
                'phrase_bonus': phrase_bonus,
                'order_bonus': order_bonus,
                'hybrid_score': hybrid_score
            })
        
        scored_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        final_results = []
        for i, result in enumerate(scored_results[:k]):
            final_results.append({
                "rank": i + 1,
                "content": result['content'],
                "similarity_score": result['similarity_score'],
                "hybrid_score": round(result['hybrid_score'], 3),
                "keyword_matches": result['keyword_score'],
                "exact_phrase": bool(result['phrase_bonus'] > 0),
                "metadata": result['metadata']
            })
        
        return final_results
    
    def export_to_json(self, pairs: List[Dict[str, str]], output_file: str = None) -> str:
        json_str = json.dumps(pairs, indent=2, ensure_ascii=False)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"Created {output_file} with {len(pairs)} title-content pairs")
        
        return json_str
    
    def get_database_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM documents")
            total_docs = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM documents WHERE metadata LIKE '%html_section%'")
            html_sections = cursor.fetchone()[0]
        
        return {
            'total_documents': total_docs,
            'html_sections': html_sections,
            'database_path': self.db_path
        }

def main():
    if len(sys.argv) != 2:
        print("Usage: python simple_parser.py <html_file>")
        print("Example: python simple_parser.py document.html")
        print("\nThis will:")
        print("1. Parse the HTML file for title-content pairs")
        print("2. Create embeddings and add to search database")
        print("3. Export pairs to JSON file")
        print("4. Enable hybrid search on the parsed content")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = input_file.replace('.html', '_pairs.json')
    
    if output_file == input_file:
        output_file = input_file + '_pairs.json'
    
    print(f"Parsing {input_file} and creating embeddings...")
    
    parser = EnhancedHTMLParser()
    pairs = parser.parse_html_file(input_file)
    
    parser.export_to_json(pairs, output_file)
    
    stats = parser.get_database_stats()
    print(f"\nSearch database updated:")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  HTML sections: {stats['html_sections']}")
    print(f"  Database: {stats['database_path']}")
    
    print(f"\nYou can now search the parsed content using:")
    print(f"  - Vector search: parser.search_similar('your query')")
    print(f"  - Hybrid search: parser.hybrid_search('your query')")
    print(f"  - Or use the existing search.py FastAPI server")

if __name__ == "__main__":
    main()
