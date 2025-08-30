# 🚀 Render Cloud Deployment Guide

## 📋 **Prerequisites**

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push your Quilt code to GitHub
3. **API Keys**: Have your Cohere API key and GitHub token ready

## 🗄️ **Step 1: Deploy PostgreSQL Database**

### **Option A: Using Render Dashboard**

1. **Go to Render Dashboard** → **New** → **PostgreSQL**
2. **Configure Database:**
   ```
   Name: quilt-postgres
   Database: quilt_embeddings
   User: quilt_user
   Region: Oregon (US West)
   Plan: Free
   ```
3. **Click "Create Database"**
4. **Save the connection details** (you'll need the DATABASE_URL)

### **Option B: Using Blueprint (Automated)**

1. **Fork/Clone** your repository to GitHub
2. **Go to Render Dashboard** → **New** → **Blueprint**
3. **Connect your GitHub repository**
4. **Render will auto-deploy** using `render.yaml`

## 🔧 **Step 2: Deploy FastAPI Backend**

### **Manual Deployment:**

1. **Go to Render Dashboard** → **New** → **Web Service**
2. **Connect GitHub Repository**
3. **Configure Service:**
   ```
   Name: quilt-api
   Environment: Python 3
   Build Command: pip install -r cloud_requirements.txt
   Start Command: python -m uvicorn cloud_updated_quilt_api:app --host 0.0.0.0 --port $PORT
   ```

4. **Environment Variables:**
   ```
   DATABASE_URL=<your_postgres_connection_string>
   COHERE_API_KEY=ivxGlP6nz7wkba0oTBuSaIYmaSQAof5lIPh2AwsO
   GITHUB_TOKEN=<your_github_token>
   PYTHON_VERSION=3.11
   ```

5. **Click "Create Web Service"**

## 🌐 **Step 3: Deploy Next.js Frontend**

1. **Go to Render Dashboard** → **New** → **Web Service**
2. **Connect GitHub Repository**
3. **Configure Service:**
   ```
   Name: quilt-frontend
   Environment: Node
   Build Command: npm install && npm run build
   Start Command: npm start
   ```

4. **Environment Variables:**
   ```
   NEXT_PUBLIC_QUILT_API_URL=<your_api_service_url>
   NODE_VERSION=18
   ```

5. **Click "Create Web Service"**

## 🔗 **Step 4: Get Your URLs**

After deployment, you'll have:

- **API**: `https://quilt-api-xyz.onrender.com`
- **Frontend**: `https://quilt-frontend-xyz.onrender.com`
- **Database**: Internal connection via DATABASE_URL

## 🧪 **Step 5: Test Your Deployment**

### **Test API Health:**
```bash
curl https://your-api-url.onrender.com/health
```

### **Test Database Connection:**
```bash
curl https://your-api-url.onrender.com/stats
```

### **Test Deployment:**
```bash
curl -X POST https://your-api-url.onrender.com/deploy \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "repo_url": "https://github.com/microsoft/vscode-docs"}'
```

## 🤖 **Step 6: Update Claude Desktop for Cloud**

Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "database-search": {
      "command": "/usr/local/bin/python3",
      "args": ["/Users/yuvraj/Desktop/Quilt/cloud_mcp_server.py"],
      "cwd": "/Users/yuvraj/Desktop/Quilt",
      "env": {
        "CLOUD_API_URL": "https://your-api-url.onrender.com"
      }
    }
  }
}
```

## 💡 **Render Free Tier Limits**

- **PostgreSQL**: 1GB storage, 97 hours/month
- **Web Services**: 750 hours/month total
- **Bandwidth**: 100GB/month
- **Build Minutes**: 500 minutes/month

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Build Failures**: Check `cloud_requirements.txt` versions
2. **Database Connection**: Verify DATABASE_URL format
3. **API Timeouts**: Render free tier has cold starts
4. **Environment Variables**: Double-check all required vars

### **Logs Access:**
- **Render Dashboard** → **Your Service** → **Logs**

## 🚀 **Production Optimizations**

For production use:

1. **Upgrade to Paid Plans** for better performance
2. **Add Redis Caching** for faster responses  
3. **Configure Custom Domains**
4. **Set up Monitoring** and alerts
5. **Enable Auto-Deploy** from GitHub

## 📊 **Monitoring Your Deployment**

- **Health Check**: `GET /health`
- **Stats**: `GET /stats` 
- **Logs**: Render Dashboard
- **Database**: Built-in Render PostgreSQL metrics

Your Quilt system will be fully cloud-hosted and accessible worldwide! 🌍
