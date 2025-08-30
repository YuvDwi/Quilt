# 🚀 Claude Desktop + MCP Database Setup (FREE!)

Claude Desktop has **native MCP support** and works perfectly with your database server.

## 📥 Install Claude Desktop

1. **Download**: https://claude.ai/download
2. **Install**: Follow the installer
3. **Sign up**: Free account (no payment needed)

## 🔧 Configure MCP Server

1. **Open Claude Desktop**
2. **Settings** → **Developer** → **Model Context Protocol**
3. **Add Server**:
   ```json
   {
     "server_name": "database_search",
     "command": "python3",
     "args": ["mcp_database_server.py"],
     "cwd": "/Users/yuvraj/Desktop/Quilt"
   }
   ```

## 🧪 Test It

Start a new conversation in Claude and try:

```
"Search my database for machine learning content"
```

```
"What information do I have about Python?"
```

```
"Show me my database statistics"
```

Claude will directly use your MCP tools! 🎉

## 🔧 Alternative: Open WebUI Setup

If you want **100% local** with multiple models:

1. **Install Ollama**:
   ```bash
   # macOS
   brew install ollama
   
   # Start Ollama
   ollama serve
   
   # Download a model
   ollama pull llama3.2
   ```

2. **Install Open WebUI**:
   ```bash
   docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway \
     -v open-webui:/app/backend/data --name open-webui \
     ghcr.io/open-webui/open-webui:main
   ```

3. **Access**: http://localhost:3000

4. **Add Custom Function** (in Open WebUI):
   ```python
   # Custom function to search your database
   def search_database(query: str) -> str:
       import requests
       response = requests.get(f"http://localhost:9000/api/search?query={query}")
       return response.json()
   ```

## 💡 Quick Comparison

| Option | Cost | Setup | MCP Support | Models |
|--------|------|-------|-------------|---------|
| **Claude Desktop** | Free | 5 min | ✅ Native | Claude 3.5 |
| **Open WebUI + Ollama** | Free | 15 min | ➕ Custom | Many local models |
| **LM Studio** | Free | 10 min | ➕ API integration | Many local models |

## 🎯 Recommendation

**Start with Claude Desktop** - it's the fastest way to get your database search working with an excellent LLM, completely free!

Then you can explore local options if you want more control or different models.
