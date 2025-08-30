# 🚀 Deploy MCP Server to Cloud & Connect ChatGPT Desktop

This guide shows you how to deploy your MCP database server to the cloud and configure ChatGPT Desktop to use it.

## 🎯 Deployment Options

### Option 1: Railway (Recommended)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up
```

### Option 2: Heroku
```bash
# 1. Create Heroku app
heroku create your-mcp-server

# 2. Set environment variables
heroku config:set DB_HOST=your-postgres-host
heroku config:set DB_NAME=quilt_embeddings
heroku config:set DB_USER=quilt_user
heroku config:set DB_PASSWORD=your_password

# 3. Deploy
git push heroku main
```

### Option 3: DigitalOcean/VPS
```bash
# 1. SSH to your server
ssh user@your-server-ip

# 2. Clone and setup
git clone your-repo
cd Quilt
pip3 install -r mcp_requirements.txt

# 3. Run with systemd or PM2
sudo systemctl enable your-mcp-service
```

## 🔧 ChatGPT Desktop Configuration

Once deployed, configure ChatGPT Desktop to use your remote server:

### Method 1: HTTP MCP Server (Easiest)

1. **Modify your deployed server** to accept HTTP connections:
```python
# Add to your deployed server
from mcp.server.fastapi import create_fastapi_app
app = create_fastapi_app(server)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

2. **Configure ChatGPT Desktop**:
   - Go to Settings → Features → Model Context Protocol
   - Add new server:
     ```
     Server Name: Remote Database Search
     Type: HTTP
     URL: https://your-deployed-url.com
     ```

### Method 2: SSH Tunnel (More Secure)

1. **Create SSH tunnel** to your deployed server:
```bash
ssh -L 8000:localhost:8000 user@your-server-ip
```

2. **Configure ChatGPT Desktop**:
   ```
   Server Name: Tunneled Database Search
   Command: ssh
   Arguments: -L 8000:localhost:8000 user@your-server-ip python3 remote_mcp_setup.py
   ```

### Method 3: WebSocket Connection

1. **Deploy with WebSocket support**:
```python
# In your deployed server
from mcp.server.websocket import WebSocketServer

async def run_websocket():
    server = WebSocketServer()
    await server.serve("0.0.0.0", 8000)
```

2. **Configure ChatGPT Desktop**:
   ```
   Server Name: WebSocket Database Search
   Type: WebSocket
   URL: wss://your-deployed-url.com:8000
   ```

## 🌍 Environment Variables for Deployment

Create `.env` file for your deployment:

```env
# Database Configuration
DB_HOST=your-postgres-host.com
DB_PORT=5432
DB_NAME=quilt_embeddings
DB_USER=quilt_user
DB_PASSWORD=your_secure_password

# Optional: API Keys if needed
OPENAI_API_KEY=your_key_if_needed
```

## 📁 Deployment Files Structure

```
your-deployment/
├── remote_mcp_setup.py      # Main MCP server
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
├── Procfile                 # For Heroku
├── railway.toml            # For Railway
└── docker-compose.yml      # For Docker
```

## 🔒 Security Considerations

### 1. Database Security
```bash
# Use connection pooling
pip install psycopg2-pool

# Set up SSL connections
DB_SSL_MODE=require
```

### 2. Authentication
```python
# Add API key authentication
@server.middleware
async def auth_middleware(request):
    api_key = request.headers.get("X-API-Key")
    if api_key != os.getenv("MCP_API_KEY"):
        raise ValueError("Invalid API key")
```

### 3. Rate Limiting
```python
# Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def search_endpoint():
    # Your search logic
```

## 🚀 Quick Deploy Script

```bash
#!/bin/bash
# quick_deploy.sh

echo "🚀 Deploying MCP Server..."

# 1. Build deployment package
tar -czf mcp-server.tar.gz remote_mcp_setup.py mcp_requirements.txt .env

# 2. Upload to server
scp mcp-server.tar.gz user@your-server:/opt/mcp/

# 3. Deploy on server
ssh user@your-server << 'EOF'
cd /opt/mcp
tar -xzf mcp-server.tar.gz
pip3 install -r mcp_requirements.txt
systemctl restart mcp-server
EOF

echo "✅ Deployment complete!"
echo "🔗 Configure ChatGPT Desktop with: https://your-server/mcp"
```

## 🧪 Testing Remote Connection

```python
# test_remote_mcp.py
import asyncio
import websockets
import json

async def test_remote_server():
    uri = "wss://your-deployed-url.com:8000"
    
    async with websockets.connect(uri) as websocket:
        # Test search
        search_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search_database",
                "arguments": {"query": "test"}
            }
        }
        
        await websocket.send(json.dumps(search_request))
        response = await websocket.recv()
        print("✅ Remote server working:", response)

# Run test
asyncio.run(test_remote_server())
```

## 💡 Usage Examples

Once deployed and configured, use ChatGPT Desktop like this:

**You**: "Search my remote database for machine learning content"

**ChatGPT**: *Connects to your deployed MCP server* → *Searches your cloud database* → "Here's what I found in your database about machine learning..."

## 🆘 Troubleshooting

### Connection Issues
```bash
# Test connectivity
curl https://your-deployed-url.com/health

# Check logs
heroku logs --tail  # For Heroku
railway logs        # For Railway
```

### Database Issues
```python
# Test database connection
python3 -c "
import psycopg2
conn = psycopg2.connect(
    host='your-host', 
    database='quilt_embeddings',
    user='quilt_user',
    password='your_password'
)
print('✅ Database connected')
"
```

### ChatGPT Desktop Issues
1. Restart ChatGPT Desktop completely
2. Check MCP server configuration
3. Verify URL/connection details
4. Test with local server first

## 🎉 Benefits of Cloud Deployment

- **24/7 Availability**: Always accessible
- **Shared Access**: Multiple users can benefit
- **Scalability**: Handle more requests
- **Backup**: Cloud provider handles infrastructure
- **Updates**: Deploy updates without user setup

Your database search is now available to ChatGPT from anywhere! 🌍
