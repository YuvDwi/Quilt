# 🚀 MCP Database Search Setup Guide

This guide shows you how to connect your PostgreSQL database to ChatGPT using Model Context Protocol (MCP).

## What is MCP?

Model Context Protocol (MCP) allows ChatGPT Desktop to directly access your local tools and data. Instead of copying/pasting or using plugins, ChatGPT can directly search your database and use that information in its responses.

## 🎯 What You Get

- **Direct Database Access**: ChatGPT can search your PostgreSQL database
- **Real-time Results**: No need to copy/paste data
- **Natural Language**: Ask ChatGPT to "search my database for X" 
- **Multiple Tools**: Search, stats, topic-based queries
- **Secure**: Runs locally, no data sent to external services

## 📋 Prerequisites

- ✅ PostgreSQL database set up (from earlier steps)
- ✅ ChatGPT Desktop application (macOS/Windows)
- ✅ Python 3.8+

## 🛠️ Installation Steps

### 1. Install MCP Dependencies
```bash
cd /Users/yuvraj/Desktop/Quilt
pip3 install -r mcp_requirements.txt
```

### 2. Test the MCP Server
```bash
python3 test_mcp_server.py
```
You should see "✅ All tests completed successfully!"

### 3. Configure ChatGPT Desktop

1. **Open ChatGPT Desktop** (download from OpenAI if needed)

2. **Go to Settings**:
   - Click the gear icon ⚙️
   - Navigate to **Features**
   - Find **Model Context Protocol**

3. **Add New MCP Server**:
   ```
   Server Name: Database Search
   Command: python3
   Arguments: mcp_database_server.py
   Working Directory: /Users/yuvraj/Desktop/Quilt
   ```

4. **Save and Restart** ChatGPT Desktop

### 4. Test the Integration

Open a new chat in ChatGPT and try:

```
"Search my database for machine learning content"
```

```
"What information do I have about Python in my database?"
```

```
"Show me my database statistics"
```

## 🔧 Available Tools

Your MCP server provides these tools to ChatGPT:

### 1. `search_database`
- **Purpose**: Search for content by query
- **Usage**: "Search my database for [topic]"
- **Parameters**: query, max_results

### 2. `get_database_stats` 
- **Purpose**: Get database statistics
- **Usage**: "Show me my database stats"
- **Returns**: Document count, recent activity, content samples

### 3. `search_by_topic`
- **Purpose**: Topic-specific search with context
- **Usage**: "Find content about [topic] in context of [context]"
- **Parameters**: topic, context (optional)

## 💡 Example Conversations

**You**: "What do I have in my database about machine learning?"

**ChatGPT**: *Uses search_database tool* → "Based on your database, here's what I found about machine learning: [relevant content from your database]..."

**You**: "How much content do I have stored?"

**ChatGPT**: *Uses get_database_stats tool* → "Your database contains 150 documents with 45 added in the last 7 days..."

## 🔧 Troubleshooting

### Server Won't Start
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Test database connection
python3 -c "import psycopg2; conn = psycopg2.connect(host='localhost', database='quilt_embeddings', user='quilt_user', password='your_secure_password'); print('✅ Database connected')"
```

### ChatGPT Can't Find Server
1. Verify the working directory path is correct
2. Check that `python3` is in your PATH
3. Restart ChatGPT Desktop completely
4. Check ChatGPT logs/console for errors

### Search Returns No Results
1. Make sure you have content in your database:
   ```bash
   python3 add_test_content.py
   ```
2. Test search directly:
   ```bash
   python3 debug_search.py
   ```

## 🌍 Sharing with Others

### Option 1: Local Network Access
```bash
# Modify mcp_database_server.py to accept connections
# Add host="0.0.0.0" to allow network access
```

### Option 2: Cloud Deployment
Deploy to Railway, Heroku, or DigitalOcean:
1. Package the MCP server
2. Set up environment variables
3. Configure database connections
4. Share the server URL

### Option 3: Export Database
```bash
# Export your database content
pg_dump quilt_embeddings > database_export.sql

# Others can import:
psql -U quilt_user -d quilt_embeddings < database_export.sql
```

## 🔒 Security Notes

- MCP server runs locally by default
- Database credentials stay on your machine
- No data sent to external services (except OpenAI for ChatGPT responses)
- Use environment variables for sensitive config

## 📁 File Structure

```
Quilt/
├── mcp_database_server.py     # Main MCP server
├── mcp_config.json           # Configuration
├── mcp_requirements.txt      # Dependencies
├── test_mcp_server.py       # Test script
└── database_config.py       # Database connection
```

## 🎉 What's Next?

Once set up, you can:

1. **Natural Database Queries**: Ask ChatGPT anything about your data
2. **Data Analysis**: "Analyze the trends in my database content"
3. **Content Discovery**: "What's the most relevant content for [topic]?"
4. **Research Assistant**: ChatGPT becomes your personal research tool

## 🆘 Need Help?

1. Run the test script: `python3 test_mcp_server.py`
2. Check the setup guide above
3. Verify all prerequisites are met
4. Test database connection separately

Your database is now directly accessible to ChatGPT! 🎉
