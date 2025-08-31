#!/usr/bin/env python3
"""
Check what was deployed to the cloud database
"""

import requests
import json

def check_cloud_deployment():
    """Check the cloud API for deployment stats"""
    
    # Replace with your actual Render API URL
    api_url = input("Enter your Render API URL (e.g., https://quilt-api-xyz.onrender.com): ")
    
    if not api_url:
        print("❌ API URL required")
        return
    
    print("🔍 CHECKING CLOUD DEPLOYMENT")
    print("=" * 40)
    
    try:
        # Check health
        print("📊 Getting database stats...")
        stats_response = requests.get(f"{api_url}/stats", timeout=30)
        stats_response.raise_for_status()
        stats = stats_response.json()
        
        print(f"\n📈 **Database Statistics:**")
        print(f"Total Documents: {stats.get('total_documents', 0)}")
        
        if 'repositories' in stats and stats['repositories']:
            print(f"\n📚 **Repositories:**")
            for repo, count in sorted(stats['repositories'].items(), key=lambda x: x[1], reverse=True):
                print(f"  - {repo}: {count} documents")
        
        # Check deployments for your user
        user_id = "YuvDwi"  # Your GitHub username
        print(f"\n🚀 **Your Deployments ({user_id}):**")
        
        deployments_response = requests.get(f"{api_url}/deployments/{user_id}", timeout=30)
        deployments_response.raise_for_status()
        deployments = deployments_response.json()
        
        if deployments.get('deployments'):
            for deployment in deployments['deployments']:
                print(f"  📦 {deployment['repo_name']}")
                print(f"     - Deployed: {deployment.get('deployed_at', 'Unknown')}")
                print(f"     - Sections: {deployment.get('sections_indexed', 0)}")
                print(f"     - Documents: {deployment.get('documents_added', 0)}")
                print(f"     - Status: {deployment.get('status', 'Unknown')}")
                print()
        else:
            print("  No deployments found")
        
        # Check health
        print("🏥 **API Health:**")
        health_response = requests.get(f"{api_url}/health", timeout=30)
        health_response.raise_for_status()
        health = health_response.json()
        
        print(f"  Status: {health.get('status', 'Unknown')}")
        print(f"  Database: {health.get('postgres', 'Unknown')}")
        print(f"  Documents: {health.get('documents_indexed', 0)}")
        print(f"  Cohere: {health.get('cohere_api', 'Unknown')}")
        
        print(f"\n✅ Your quilt-test content is ready for Claude Desktop!")
        
    except Exception as e:
        print(f"❌ Error checking deployment: {e}")

if __name__ == "__main__":
    check_cloud_deployment()
