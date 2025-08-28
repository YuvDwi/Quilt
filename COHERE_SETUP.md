# Cohere Embeddings Setup

## 🎯 Quick Setup Guide

### 1. Get Your Cohere API Key
1. Go to https://cohere.ai
2. Sign up for a free account
3. Navigate to Dashboard → API Keys
4. Copy your API key

### 2. Set Environment Variable

**For Railway:**
1. Go to your Railway project dashboard
2. Click on "Variables" tab
3. Add: `COHERE_API_KEY` = `your_api_key_here`

**For Local Development:**
```bash
export COHERE_API_KEY=your_api_key_here
```

### 3. Free Tier Limits
- ✅ **100,000 embeddings per month** (FREE)
- ✅ **No credit card required** for free tier
- ✅ **Perfect for testing and small projects**

### 4. Usage Estimates
- **Small repo (5 files):** ~50 embeddings
- **Medium repo (20 files):** ~200 embeddings  
- **Large repo (100 files):** ~1,000 embeddings

### 5. After Free Tier
- **Cost:** $0.10 per 1 million embeddings
- **Still very cheap** for most use cases

## 🚀 Benefits

- ✅ **Real vector embeddings** (better than TF-IDF)
- ✅ **No deployment size issues** (API-based)
- ✅ **Excellent search quality**
- ✅ **100K free embeddings/month**
- ✅ **Easy to set up**

## 🔧 Technical Details

- **Model:** `embed-english-light-v3.0`
- **Dimension:** 1024
- **Input types:** `search_document` and `search_query`
- **Optimized for:** Semantic search and retrieval

## 🆘 Troubleshooting

**If embeddings aren't working:**
1. Check your API key is set correctly
2. Check Railway logs for error messages
3. The system will fall back to TF-IDF search if Cohere fails

**To verify setup:**
- Check `/stats` endpoint - should show "Cohere embed-english-light-v3.0"
- If it shows "TF-IDF fallback", your API key isn't working
