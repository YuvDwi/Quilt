# Quilt Test Repository

This repository is used to test the Quilt vector indexing system.

## What is Quilt?

Quilt automatically indexes HTML content with vector embeddings to enable instant semantic search. It revolutionizes RAG (Retrieval-Augmented Generation) systems by providing pre-computed vectors instead of requiring real-time embedding generation.

## Test Content

The `test_content.html` file contains HTML with `data-llm` attributes:
- `data-llm="title"` - Marks content titles/headings
- `data-llm="content"` - Marks content sections to be indexed

## How It Works

1. When code is pushed to this repository, Quilt's GitHub App receives a webhook
2. Quilt downloads and parses the HTML files
3. Content with `data-llm` attributes gets extracted
4. TF-IDF vectors are generated for semantic search
5. Content is stored in Quilt's vector database
6. The content becomes instantly searchable via Quilt's API

## Testing Quilt

After pushing content, you can search it at:
- `https://quilt-production.up.railway.app/search?query=vector%20database&search_type=hybrid`
- `https://quilt-production.up.railway.app/search?query=machine%20learning&search_type=vector`

## Repository Status

Check if this repository is indexed:
- `https://quilt-production.up.railway.app/repositories`