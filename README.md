# Quilt

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/821cde50-8f3d-41e9-87ac-c9b235e9540b" />

Quilt is an open-source deployment system that transforms websites and code repositories into **Claude Desktop MCP-native data sources**.  
It ingests repos, extracts tagged content, computes semantic embeddings using **Cohere**, and publishes them to a searchable API so LLMs can query them instantly—without building custom APIs.

---

# Quilt Overview

Quilt reduces the gap between human-facing content and machine-facing interfaces by:

- **Making websites MCP-native**: Any GitHub repo can be deployed and indexed for Claude Desktop search.  
- **Eliminating manual indexing**: Content is automatically extracted and vectorized on deployment.  
- **Precomputing embeddings**: **Cohere embeddings** are generated ahead of time for instant semantic queries.  
- **GitHub OAuth integration**: Simple authentication and repository selection through GitHub.  

_Think: "Don't just deploy to the web—**deploy to LLMs** with Quilt."_

---

# Quilt Advantages

Quilt creates benefits for three groups at once:

- **For LLMs & Claude Desktop** → Faster and more efficient retrieval. Pre-indexed vectors mean no wasted compute or latency at query time.  
- **For Content Owners** → A simple way to make their GitHub repositories instantly accessible to Claude Desktop. Just tag content with `data-llm` attributes and deploy.  
- **For Developers** → No need to build or maintain custom search APIs. Quilt surfaces data through a unified interface automatically.  

Additional benefits:  
- **GitHub-native workflow** → Deploy directly from your existing repositories.  
- **Cohere embeddings** → State-of-the-art semantic search using `embed-english-v3.0`.  
- **PostgreSQL storage** → Scalable vector database with full-text search capabilities.  
- **Real-time deployment** → Push changes and see them reflected in search immediately.  
- **Web dashboard** → Visual interface for managing deployments and viewing statistics.  

---

# How Quilt Works

Quilt's architecture combines modern NLP with GitHub-native developer workflows:

1. **GitHub Authentication** – Users authenticate via GitHub OAuth and select repositories.  
2. **Repository Deployment** – Selected repos are fetched and processed via GitHub API.  
3. **Content Parsing** – HTML/JSX/React files are scanned for `data-llm` attributes.  
4. **Content Extraction** – Elements with `data-llm` tags have their text content extracted.  
5. **Vectorization** – **Cohere's embed-english-v3.0** generates semantic embeddings.  
6. **Database Storage** – Content, embeddings, and metadata stored in **PostgreSQL**.  
7. **Search API** – RESTful endpoints provide vector, keyword, and hybrid search.  
8. **MCP Integration** – Claude Desktop can search through deployed content via MCP server.  

**Tech stack**:  
- **Frontend** → Next.js with React and Tailwind CSS  
- **Backend** → FastAPI with Python  
- **Database** → PostgreSQL with vector search capabilities  
- **Embeddings** → Cohere API (`embed-english-v3.0`)  
- **Deployment** → Render (backend) + Vercel (frontend)  

---

# Quilt Deployment Flow

1. **GitHub OAuth** – Authenticate and authorize Quilt to access repositories.  
2. **Repository Selection** – Choose which repos to deploy from your GitHub account.  
3. **Content Processing** – Quilt fetches repo files and scans for `data-llm` attributes.  
4. **Text Extraction** – Tagged content is extracted and cleaned.  
5. **Embedding Generation** – Cohere API generates semantic vectors for each content section.  
6. **Database Indexing** – Content, embeddings, and metadata stored in PostgreSQL.  
7. **Search Availability** – Content becomes searchable via API and Claude Desktop MCP.  
8. **Dashboard Monitoring** – View deployment status and search statistics in web interface.  

---

# Quilt Content Annotation

Use `data-llm` attributes in your HTML/JSX to define searchable regions:

- `data-llm="title"` → For titles/headings  
- `data-llm="content"` → For descriptive sections  
- `data-llm="description"` → For detailed explanations  

**Example (React component):**
```jsx
export default function FeatureSection() {
  return (
    <div>
      <h2 data-llm="title">Vector Search Technology</h2>
      <p data-llm="content">
        Quilt uses Cohere embeddings to enable semantic search across 
        your deployed repositories, making content instantly discoverable.
      </p>
      <div data-llm="description">
        The system processes HTML and JSX files, extracting tagged content
        and generating high-quality vector representations for Claude Desktop.
      </div>
    </div>
  )
}
```

**Example (HTML file):**
```html
<h1 data-llm="title">Getting Started with Quilt</h1>
<p data-llm="content">Deploy your repositories to make them searchable by Claude Desktop.</p>
<section data-llm="description">
  Quilt automatically processes your content and creates semantic embeddings,
  enabling powerful search capabilities for AI assistants.
</section>
```

---

# API Endpoints

Quilt provides several REST endpoints for search and management:

- **POST /deploy** → Deploy a GitHub repository  
- **GET /search** → Search all deployed content  
- **GET /search/{user_id}** → Search specific user's content  
- **GET /deployments/{user_id}** → List user's deployments  
- **GET /stats** → Get database statistics  
- **DELETE /deployments/{deployment_id}** → Remove a deployment  

---

# Getting Started

1. **Visit the Quilt web interface**
2. **Authenticate with GitHub** using OAuth
3. **Select repositories** you want to make searchable
4. **Deploy** with one click
5. **Search your content** via the web interface or Claude Desktop

The deployed content becomes immediately available for semantic search through both the web API and Claude Desktop's MCP integration.