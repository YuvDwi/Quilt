#!/usr/bin/env python3
"""
Auto Sync Websites
Automatically sync content from your deployed websites on a schedule
"""

import os
import time
import schedule
from website_content_crawler import WebsiteCrawler
import psycopg2
from datetime import datetime

def sync_websites():
    """Sync all your deployed websites"""
    print(f"\n🔄 Auto-sync started at {datetime.now()}")
    
    # Your deployed websites - UPDATE THESE WITH YOUR ACTUAL URLS
    websites = [
        {
            'url': 'https://your-quilt-app.vercel.app',
            'max_pages': 15
        },
        {
            'url': 'https://your-portfolio.netlify.app',
            'max_pages': 10
        },
        {
            'url': 'https://your-blog.railway.app',
            'max_pages': 25
        }
        # Add all your deployed websites here
    ]
    
    crawler = WebsiteCrawler()
    
    # Get current count
    try:
        conn = psycopg2.connect(**crawler.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        before_count = cursor.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Crawl all websites
    for site in websites:
        try:
            print(f"\n🌐 Syncing: {site['url']}")
            crawler.crawl_website(site['url'], site['max_pages'])
        except Exception as e:
            print(f"❌ Error syncing {site['url']}: {e}")
    
    # Show results
    try:
        conn = psycopg2.connect(**crawler.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        after_count = cursor.fetchone()[0]
        conn.close()
        
        new_content = after_count - before_count
        print(f"\n✅ Sync complete!")
        print(f"📊 Total documents: {after_count}")
        print(f"📈 New content: {new_content} documents")
        
        if new_content > 0:
            print("🎉 Claude Desktop can now search your latest website content!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def main():
    print("🔄 AUTO-SYNC SCHEDULER")
    print("=" * 50)
    print("This will automatically sync your website content to the database.")
    print("Claude Desktop will always have access to your latest content!")
    print()
    
    # Schedule sync every 6 hours
    schedule.every(6).hours.do(sync_websites)
    
    # Also schedule daily at 3 AM
    schedule.every().day.at("03:00").do(sync_websites)
    
    print("⏰ Scheduled sync:")
    print("   - Every 6 hours")
    print("   - Daily at 3:00 AM")
    print()
    print("🚀 Starting scheduler... (Press Ctrl+C to stop)")
    
    # Run initial sync
    sync_websites()
    
    # Keep running scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Scheduler stopped.")
