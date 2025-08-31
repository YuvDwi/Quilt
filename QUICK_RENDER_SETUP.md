# 🚀 QUICK RENDER SETUP - 5 MINUTES

Your code is already pushed to GitHub! Now let's deploy to Render:

## 🌐 **Step 1: Go to Render**
👉 **Open**: https://render.com
👉 **Sign up/Login** with GitHub

## 🗄️ **Step 2: Create PostgreSQL Database**

1. **Click**: `New +` → `PostgreSQL`
2. **Fill in**:
   - Name: `quilt-postgres`
   - Database: `quilt_embeddings` 
   - User: `quilt_user`
   - Region: `Oregon (US West)`
   - Plan: `Free`
3. **Click**: `Create Database`
4. **Copy the DATABASE_URL** (you'll need it next)

## ⚡ **Step 3: Deploy API Service**

1. **Click**: `New +` → `Web Service`
2. **Connect**: Your GitHub repository (`YuvDwi/Quilt`)
3. **Configure**:
   - Name: `quilt-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r cloud_requirements.txt`
   - Start Command: `python -m uvicorn cloud_updated_quilt_api:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**:
   ```
   DATABASE_URL = <paste_your_postgres_url_here>
   COHERE_API_KEY = ivxGlP6nz7wkba0oTBuSaIYmaSQAof5lIPh2AwsO
   GITHUB_TOKEN = <your_github_token>
   PYTHON_VERSION = 3.11
   ```

5. **Click**: `Create Web Service`

## 🌐 **Step 4: Deploy Frontend**

1. **Click**: `New +` → `Web Service`
2. **Connect**: Same GitHub repository
3. **Configure**:
   - Name: `quilt-frontend`
   - Environment: `Node`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`

4. **Environment Variables**:
   ```
   NEXT_PUBLIC_QUILT_API_URL = <your_api_url_from_step_3>
   NODE_VERSION = 18
   ```

5. **Click**: `Create Web Service`

## 🧪 **Step 5: Test Your Deployment**

After both services deploy (5-10 minutes):

```bash
# Test API health
curl https://your-api-name.onrender.com/health

# Test database stats  
curl https://your-api-name.onrender.com/stats
```

## 🤖 **Step 6: Update Claude Desktop**

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "database-search": {
      "command": "/usr/local/bin/python3",
      "args": ["/Users/yuvraj/Desktop/Quilt/cloud_mcp_server.py"],
      "cwd": "/Users/yuvraj/Desktop/Quilt",
      "env": {
        "CLOUD_API_URL": "https://your-api-name.onrender.com"
      }
    }
  }
}
```

## ✅ **You're Done!**

- 🌐 **Frontend**: `https://quilt-frontend-xyz.onrender.com`
- ⚡ **API**: `https://quilt-api-xyz.onrender.com` 
- 🗄️ **Database**: Managed PostgreSQL
- 🤖 **Claude Desktop**: Searches your cloud data

**Your Quilt system is now live on the cloud!** 🎉
