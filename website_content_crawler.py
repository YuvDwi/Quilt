#!/usr/bin/env python3
"""
Website Content Crawler
Automatically extracts content from your deployed websites and adds to database
"""

import requests
import psycopg2
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
import hashlib

class WebsiteCrawler:
    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "port": "5432",
            "database": "quilt_embeddings",
            "user": "quilt_user",
            "password": "your_secure_password"
        }
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Quilt Content Crawler 1.0'
        })

    def extract_content(self, url):
        """Extract text content from a webpage"""
        try:
            print(f"📄 Crawling: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            title = soup.find('title').get_text() if soup.find('title') else ""
            
            # Get main content (prioritize main, article, or body)
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            content = main_content.get_text() if main_content else soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                'url': url,
                'title': title.strip(),
                'content': content,
                'extracted_at': datetime.now().isoformat(),
                'content_hash': hashlib.md5(content.encode()).hexdigest()
            }
            
        except Exception as e:
            print(f"❌ Error crawling {url}: {e}")
            return None

    def save_to_database(self, page_data):
        """Save extracted content to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check if content already exists (avoid duplicates)
            cursor.execute(
                "SELECT id FROM documents WHERE doc_metadata->>'url' = %s",
                (page_data['url'],)
            )
            
            if cursor.fetchone():
                print(f"📋 Already exists: {page_data['url']}")
                conn.close()
                return False
            
            # Insert new content
            metadata = {
                'url': page_data['url'],
                'title': page_data['title'],
                'source': 'website_crawler',
                'extracted_at': page_data['extracted_at'],
                'content_hash': page_data['content_hash']
            }
            
            cursor.execute(
                """INSERT INTO documents (content, doc_metadata, created_at) 
                   VALUES (%s, %s, %s)""",
                (page_data['content'], json.dumps(metadata), datetime.now())
            )
            
            conn.commit()
            conn.close()
            print(f"✅ Saved: {page_data['title']} ({page_data['url']})")
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False

    def crawl_website(self, base_url, max_pages=10):
        """Crawl a website starting from base_url"""
        print(f"🚀 Starting crawl of: {base_url}")
        
        urls_to_visit = [base_url]
        pages_crawled = 0
        
        while urls_to_visit and pages_crawled < max_pages:
            url = urls_to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
                
            self.visited_urls.add(url)
            
            # Extract content
            page_data = self.extract_content(url)
            if page_data and len(page_data['content']) > 100:  # Only save substantial content
                if self.save_to_database(page_data):
                    pages_crawled += 1
            
            # Add delay to be respectful
            time.sleep(1)
        
        print(f"🎉 Crawl complete! Processed {pages_crawled} pages")

    def crawl_multiple_sites(self, sites):
        """Crawl multiple websites"""
        for site in sites:
            print(f"\n{'='*50}")
            self.crawl_website(site['url'], site.get('max_pages', 5))
            time.sleep(2)  # Pause between sites

def main():
    crawler = WebsiteCrawler()
    
    # Your deployed websites - ADD YOUR ACTUAL URLS HERE
    websites = [
        {
            'url': 'https://your-app.vercel.app',
            'max_pages': 10
        },
        {
            'url': 'https://your-blog.netlify.app', 
            'max_pages': 20
        },
        # Add more of your deployed sites here
    ]
    
    print("🕷️  WEBSITE CONTENT CRAWLER")
    print("=" * 50)
    print("This will crawl your deployed websites and add content to your database.")
    print("Claude Desktop will then be able to search this live content!")
    print()
    
    # Show current database stats
    try:
        conn = psycopg2.connect(**crawler.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        current_count = cursor.fetchone()[0]
        print(f"📊 Current database: {current_count} documents")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return
    
    # Crawl websites
    if websites[0]['url'] == 'https://your-app.vercel.app':
        print("⚠️  Please edit this script and add your actual website URLs!")
        print("   Replace the example URLs with your deployed websites.")
        return
    
    crawler.crawl_multiple_sites(websites)
    
    # Show final stats
    try:
        conn = psycopg2.connect(**crawler.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        final_count = cursor.fetchone()[0]
        print(f"\n📊 Final database: {final_count} documents")
        print(f"📈 Added: {final_count - current_count} new documents")
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    main()
