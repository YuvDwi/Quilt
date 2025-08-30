#!/bin/bash
# 🚀 Quick Deploy to Render Script

echo "🌐 DEPLOYING QUILT TO RENDER CLOUD"
echo "=================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial Quilt deployment"
fi

# Check if GitHub remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ No GitHub remote found!"
    echo "Please:"
    echo "1. Create a GitHub repository"
    echo "2. Add it as remote: git remote add origin https://github.com/yourusername/quilt.git"
    echo "3. Push your code: git push -u origin main"
    echo "4. Then run this script again"
    exit 1
fi

echo "✅ Git repository ready"

# Push latest changes
echo "📤 Pushing latest changes to GitHub..."
git add .
git commit -m "Deploy to Render - $(date)" || echo "No changes to commit"
git push origin main || git push origin master

echo ""
echo "🎯 NEXT STEPS:"
echo "=============="
echo ""
echo "1. 🌐 Go to https://render.com and sign up/login"
echo ""
echo "2. 🗄️ Create PostgreSQL Database:"
echo "   - Click 'New' → 'PostgreSQL'"
echo "   - Name: quilt-postgres"
echo "   - Database: quilt_embeddings"
echo "   - User: quilt_user"
echo "   - Plan: Free"
echo "   - Click 'Create Database'"
echo ""
echo "3. 🔧 Deploy API Service:"
echo "   - Click 'New' → 'Web Service'"
echo "   - Connect your GitHub repository"
echo "   - Name: quilt-api"
echo "   - Environment: Python 3"
echo "   - Build Command: pip install -r cloud_requirements.txt"
echo "   - Start Command: python -m uvicorn cloud_updated_quilt_api:app --host 0.0.0.0 --port \$PORT"
echo ""
echo "4. 🔑 Set Environment Variables for API:"
echo "   DATABASE_URL=<your_postgres_connection_string>"
echo "   COHERE_API_KEY=ivxGlP6nz7wkba0oTBuSaIYmaSQAof5lIPh2AwsO"
echo "   GITHUB_TOKEN=<your_github_token>"
echo "   PYTHON_VERSION=3.11"
echo ""
echo "5. 🌐 Deploy Frontend:"
echo "   - Click 'New' → 'Web Service'"
echo "   - Connect same GitHub repository"
echo "   - Name: quilt-frontend"
echo "   - Environment: Node"
echo "   - Build Command: npm install && npm run build"
echo "   - Start Command: npm start"
echo ""
echo "6. 🔑 Set Environment Variables for Frontend:"
echo "   NEXT_PUBLIC_QUILT_API_URL=<your_api_service_url>"
echo "   NODE_VERSION=18"
echo ""
echo "7. 🧪 Test Your Deployment:"
echo "   curl https://your-api-url.onrender.com/health"
echo ""
echo "8. 🤖 Update Claude Desktop:"
echo "   Edit: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "   Update CLOUD_API_URL to your Render API URL"
echo ""
echo "📖 Full guide: See RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "🚀 Your Quilt system will be live on the cloud!"
