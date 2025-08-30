#!/usr/bin/env python3
"""
Test the integrated Quilt deployment system
"""

from integrated_quilt_deployer import IntegratedQuiltDeployer
import psycopg2

def test_deployment():
    print("🧪 Testing Integrated Quilt Deployment System")
    print("=" * 60)
    
    # Initialize deployer
    deployer = IntegratedQuiltDeployer()
    
    # Check PostgreSQL connection
    try:
        conn = psycopg2.connect(**deployer.pg_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        initial_count = cursor.fetchone()[0]
        print(f"📊 Initial PostgreSQL documents: {initial_count}")
        conn.close()
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return
    
    # Test deployment with a small repository
    test_repo = "https://github.com/microsoft/vscode-docs"  # Use existing working repo
    test_user = "test_user_integration"
    
    print(f"\n🚀 Testing deployment of: {test_repo}")
    print(f"👤 User: {test_user}")
    
    # Deploy repository
    result = deployer.deploy_repository(test_user, test_repo, "")
    
    print(f"\n📋 Deployment Result:")
    print(f"   Status: {result['status']}")
    print(f"   Repository: {result.get('repository', 'N/A')}")
    print(f"   Documents added: {result.get('postgres_documents', 0)}")
    
    if result['status'] == 'success':
        # Check final count
        try:
            conn = psycopg2.connect(**deployer.pg_config)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            final_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM documents 
                WHERE doc_metadata->>'source' = 'quilt_deployment'
            """)
            quilt_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"\n📊 Final PostgreSQL documents: {final_count}")
            print(f"📊 Quilt deployment documents: {quilt_count}")
            print(f"📈 Documents added: {final_count - initial_count}")
            
            if final_count > initial_count:
                print("\n🎉 SUCCESS! Content indexed into PostgreSQL")
                print("🔍 Claude Desktop can now search this repository content!")
            else:
                print("\n⚠️  No new documents added (might be duplicates)")
            
        except Exception as e:
            print(f"❌ Error checking final count: {e}")
    
    # Test getting deployments
    print(f"\n📋 Getting deployments for user: {test_user}")
    deployments = deployer.get_deployments(test_user)
    print(f"   Found {len(deployments)} deployments")
    
    for i, dep in enumerate(deployments):
        print(f"   {i+1}. {dep['repo_name']} - {dep['postgres_documents']} docs")

if __name__ == "__main__":
    test_deployment()
