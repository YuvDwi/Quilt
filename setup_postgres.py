"""
PostgreSQL Setup Script for Quilt Embeddings

This script helps you set up PostgreSQL for your searchable embeddings.
Run this after installing PostgreSQL on your system.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_postgresql_installed():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL is not installed or not in PATH")
        return False

def create_database_and_user():
    """Create database and user for Quilt"""
    print("\n🔧 Setting up PostgreSQL database and user...")
    
    commands = [
        "CREATE DATABASE quilt_embeddings;",
        "CREATE USER quilt_user WITH PASSWORD 'your_secure_password';",
        "GRANT ALL PRIVILEGES ON DATABASE quilt_embeddings TO quilt_user;",
        "\\c quilt_embeddings",
        "GRANT ALL ON SCHEMA public TO quilt_user;"
    ]
    
    print("\nPlease run the following commands in psql as a superuser:")
    print("First, connect to PostgreSQL:")
    print("  psql postgres")
    print("\nThen run these commands:")
    for cmd in commands:
        print(f"  {cmd}")
    print("\nFinally, exit psql:")
    print("  \\q")
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from env.example")
        print("⚠️ Please update the database credentials and API keys in .env")
    elif env_file.exists():
        print("ℹ️ .env file already exists")
    else:
        print("⚠️ No env.example found to copy from")

def install_python_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False

def test_connection():
    """Test PostgreSQL connection"""
    print("\n🔍 Testing PostgreSQL connection...")
    try:
        from database_config import engine, create_tables
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT version();")
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
        
        # Create tables
        create_tables()
        print("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        print("Please check your database configuration in .env")
        return False

def main():
    """Main setup function"""
    print("🚀 PostgreSQL Setup for Quilt Embeddings")
    print("=" * 50)
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installed():
        print("\nTo install PostgreSQL:")
        print("  macOS: brew install postgresql")
        print("  Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        print("  Windows: Download from https://www.postgresql.org/download/")
        return False
    
    # Create database and user
    create_database_and_user()
    
    # Install Python dependencies
    if not install_python_dependencies():
        return False
    
    # Create .env file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Start PostgreSQL service if not running")
    print("2. Run the psql commands shown above to create database and user")
    print("3. Update your .env file with correct database credentials")
    print("4. Test the setup by running: python test_postgres_setup.py")
    print("5. Migrate existing data by running: python migrate_to_postgres.py")
    
    return True

if __name__ == "__main__":
    main()
