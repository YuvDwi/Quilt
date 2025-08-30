# 🌐 Web App Integration Guide

## 🎯 **What We've Done:**

✅ **Migrated quilt-test data** from SQLite to PostgreSQL  
✅ **Started integrated API** server on http://localhost:8000  
✅ **Verified health** - 91 documents in PostgreSQL database  

## 🔧 **To Complete Integration:**

### **1. Update Web App Environment**

Create or update your `.env.local` file in the project root:

```bash
# In /Users/yuvraj/Desktop/Quilt/.env.local
NEXT_PUBLIC_QUILT_API_URL=http://localhost:8000
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### **2. Restart Your Next.js App**

```bash
# Stop current Next.js if running
pkill -f "next"

# Start with new environment
npm run dev
```

### **3. Test the Integration**

1. **Open your web app** (usually http://localhost:3000)
2. **Deploy a repository** through the dashboard
3. **Check Claude Desktop** - new content should be searchable immediately

## 🔍 **Current Database Status:**

```
Total Documents in PostgreSQL: 91
├── quilt-test (migrated): 6 documents ✅
├── microsoft/vscode-docs: 50 documents ✅  
├── vscode-docs: 29 documents ✅
└── test data: 6 documents ✅
```

## 🤖 **Claude Desktop Test:**

Try these searches in Claude Desktop:
- "Search my database for machine learning content"
- "What is supervised learning in my quilt-test data?"
- "Find information about reinforcement learning"

## 🔧 **API Endpoints:**

Your web app now uses:
- **Deploy**: POST http://localhost:8000/deploy
- **Deployments**: GET http://localhost:8000/deployments/{user}
- **Health**: GET http://localhost:8000/health
- **Stats**: GET http://localhost:8000/stats

## ✨ **What Changed:**

### **Before:**
Web App → Old API → SQLite → Claude can't search

### **After:**
Web App → Integrated API → PostgreSQL → Claude Desktop searches ✅

All new deployments will automatically be indexed into PostgreSQL with Cohere embeddings!
