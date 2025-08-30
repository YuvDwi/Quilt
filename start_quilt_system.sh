#!/bin/bash
# 🚀 Quilt System Startup Script

echo "🔄 Starting Quilt System..."
echo "=================================="

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 -U quilt_user > /dev/null 2>&1; then
    echo "❌ PostgreSQL not running. Start with:"
    echo "   brew services start postgresql@15"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Kill any existing API servers
pkill -f "updated_quilt_api.py" 2>/dev/null || true
pkill -f "quilt_react_api.py" 2>/dev/null || true

# Wait a moment
sleep 2

# Start the integrated API
echo "🚀 Starting Integrated Quilt API..."
python3 updated_quilt_api.py &
API_PID=$!

# Wait for startup
sleep 3

# Test the API
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Integrated API running on http://localhost:8000"
    echo "📊 Database status:"
    curl -s http://localhost:8000/health | python3 -m json.tool
    
    echo ""
    echo "🌐 NEXT STEPS:"
    echo "1. Restart your Next.js web app: npm run dev"
    echo "2. Test Claude Desktop search"
    echo "3. Deploy new repositories through the web app"
    echo ""
    echo "🔍 Claude Desktop should now find your quilt-test content!"
else
    echo "❌ API failed to start"
    kill $API_PID 2>/dev/null || true
    exit 1
fi
