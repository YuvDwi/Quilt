# Quilt

A GitHub App that automatically indexes HTML content with `data-llm` attributes, creating a centralized vector database for efficient content retrieval.

## What Quilt Does

- **Automatically indexes** HTML content when code is pushed to GitHub
- **Parses** `data-llm="title"` and `data-llm="content"` attributes
- **Creates vector embeddings** for instant search
- **Eliminates RAG inefficiency** by pre-indexing content

## How It Works

1. Install Quilt GitHub App on your repositories
2. Add `data-llm` attributes to your HTML:
   ```html
   <div data-llm="title">Section Title</div>
   <div data-llm="content">Section content...</div>
   ```
3. Push code → Quilt automatically indexes it
4. Content becomes instantly searchable

## Architecture

- **GitHub App** (`quilt_github_app.py`) - Webhook handler and HTML processor
- **Quilt API** (`quilt_api.py`) - Database storage and management
- **HTML Parser** (`simple_parser.py`) - Content extraction and embedding

## Setup

1. Create a GitHub App
2. Set webhook URL to your deployed Quilt instance
3. Install on repositories you want to index
4. Add `data-llm` attributes to HTML files

## The Future of Content Indexing

Quilt creates a standardized way for all web content to be pre-indexed and instantly searchable, eliminating the need for repeated embedding and API calls.

