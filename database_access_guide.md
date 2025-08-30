# 🗄️ Database Access Guide

Your Quilt system uses two databases:

## 📊 **PostgreSQL** (Main Search Database)
**What it contains:** All indexed content that Claude Desktop searches
- **Location:** `localhost:5432`
- **Database:** `quilt_embeddings`
- **Username:** `quilt_user`
- **Password:** `your_secure_password`

### **Quick Access:**
```bash
# Command line access
psql postgresql://quilt_user:your_secure_password@localhost:5432/quilt_embeddings

# View all documents
psql postgresql://quilt_user:your_secure_password@localhost:5432/quilt_embeddings -c "SELECT COUNT(*), doc_metadata->>'source' FROM documents GROUP BY doc_metadata->>'source';"

# Search content
psql postgresql://quilt_user:your_secure_password@localhost:5432/quilt_embeddings -c "SELECT doc_metadata->>'file_path', LENGTH(content) FROM documents WHERE LOWER(content) LIKE '%copilot%' LIMIT 5;"
```

### **GUI Tools:**
1. **pgAdmin** - Download from https://www.pgadmin.org/
2. **DBeaver** - Download from https://dbeaver.io/
3. **TablePlus** - Download from https://tableplus.com/ (Mac)

**Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `quilt_embeddings`
- Username: `quilt_user`
- Password: `your_secure_password`

## 🗃️ **SQLite** (Deployment Tracking)
**What it contains:** Tracks which repositories have been deployed
- **File:** `/Users/yuvraj/Desktop/Quilt/quilt_deployments.db`

### **Quick Access:**
```bash
# Command line access
sqlite3 quilt_deployments.db

# View deployments
sqlite3 quilt_deployments.db "SELECT * FROM deployments;"

# View deployment stats
sqlite3 quilt_deployments.db "SELECT user_id, COUNT(*), SUM(pg_documents_added) FROM deployments GROUP BY user_id;"
```

### **GUI Tools:**
1. **DB Browser for SQLite** - Download from https://sqlitebrowser.org/
2. **SQLiteStudio** - Download from https://sqlitestudio.pl/

## 🔍 **Current Database Contents:**

### PostgreSQL (`quilt_embeddings`):
- **Total Documents:** 85
- **Quilt Deployments:** 50 documents (VS Code blogs)
- **GitHub Repo:** 29 documents (VS Code docs)
- **Test Data:** 6 documents

### SQLite (`quilt_deployments.db`):
- **Total Deployments:** Tracks deployment history
- **Columns:** repo_name, user_id, deployed_at, pg_documents_added

## 🧪 **Quick Database Viewer:**

Run this script to explore your data:
```bash
python3 database_viewer.py
```

## 🔍 **What Claude Desktop Searches:**

Claude Desktop searches the **PostgreSQL database** through the MCP server. It can find:
- VS Code blog posts about Copilot, extensions, remote development
- Technical documentation and tutorials
- Code examples and best practices
- Any content you deploy through Quilt

## 📈 **Monitoring Your Database:**

```bash
# Check database size
psql postgresql://quilt_user:your_secure_password@localhost:5432/quilt_embeddings -c "SELECT pg_size_pretty(pg_database_size('quilt_embeddings'));"

# Check recent additions
psql postgresql://quilt_user:your_secure_password@localhost:5432/quilt_embeddings -c "SELECT COUNT(*), DATE(created_at) FROM documents GROUP BY DATE(created_at) ORDER BY DATE(created_at) DESC LIMIT 7;"
```
