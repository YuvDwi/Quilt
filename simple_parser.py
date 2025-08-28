#!/usr/bin/env python3

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import json
import sqlite3
import re
from typing import List, Dict, Any, Optional
from hybrid_vector_search import HybridVectorSearch

class EnhancedHTMLParser:
    def __init__(self):
        # Lazy initialization to speed up startup
        self.search_engine = None
        self.db_path = "search_data.db"
    
    def get_search_engine(self):
        """Lazy initialization of search engine"""
        if self.search_engine is None:
            try:
                self.search_engine = HybridVectorSearch()
                print("✅ HTML Parser: Search engine initialized")
            except Exception as e:
                print(f"⚠️ HTML Parser: Search engine initialization failed: {e}")
                # Create a dummy object for fallback
                class DummySearchEngine:
                    def add_document(self, content, metadata=None):
                        pass
                self.search_engine = DummySearchEngine()
        return self.search_engine
    
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
        search_engine = self.get_search_engine()
        search_engine.add_document(content, metadata)
    
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
        return self.search_engine.search_similar(query_text, k)
    
    def hybrid_search(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        return self.search_engine.hybrid_search(query_text, k)
    
    def export_to_json(self, pairs: List[Dict[str, str]], output_file: str = None) -> str:
        json_str = json.dumps(pairs, indent=2, ensure_ascii=False)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"Created {output_file} with {len(pairs)} title-content pairs")
        
        return json_str
    
    def get_database_stats(self) -> Dict[str, Any]:
        stats = self.search_engine.list_documents()
        
        html_sections = sum(1 for doc in stats['documents'] 
                           if doc.get('metadata', {}).get('type') == 'html_section')
        
        return {
            'total_documents': stats['total_count'],
            'html_sections': html_sections,
            'vectorized': stats['vectorized'],
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
