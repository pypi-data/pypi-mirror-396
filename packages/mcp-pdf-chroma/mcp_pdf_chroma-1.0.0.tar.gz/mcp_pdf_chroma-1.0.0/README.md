# MCP PDF ChromaDB Server

A Python-based Model Context Protocol (MCP) server that provides PDF document processing, vectorization, and semantic search capabilities using ChromaDB with local embeddings.

## Features

- **PDF Loading**: Download and process PDFs from URLs
- **Local Embeddings**: Uses sentence-transformers for local embedding generation (no API required)
- **Persistent Storage**: ChromaDB for vector storage with metadata
- **Semantic Search**: Search documents using natural language queries
- **Page Extraction**: Retrieve specific pages from loaded PDFs
- **Metadata Tracking**: In-memory metadata storage with persistence
- **Call Logging**: Automatic logging of all PDF processing and search queries to `call_log.txt`

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install from PyPI (Recommended)

```bash
# Install the package
pip install mcp-pdf-chroma

# Or install with dev dependencies
pip install mcp-pdf-chroma[dev]
```

### Install from source

```bash
git clone <repository-url>
cd mcp_pdf_chroma

# Install dependencies
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in the project root (optional):

```bash
# Database paths
CHROMA_DB_PATH=./chroma_db
PDF_CACHE_DIR=./pdf_cache
METADATA_PERSISTENCE_FILE=./metadata_store.json

# Embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Text processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Limits
MAX_PDF_SIZE_MB=50
```

## Usage

### Running the Server

```bash
# Run as MCP server (stdio)
python -m mcp_pdf_chroma.server

# Or use the installed script
mcp-pdf-chroma
```

### MCP Client Configuration

Add to your MCP client settings (e.g., Claude Desktop):

**If installed from PyPI:**
```json
{
  "mcpServers": {
    "pdf-chroma": {
      "command": "mcp-pdf-chroma"
    }
  }
}
```

**If installed from source:**
```json
{
  "mcpServers": {
    "pdf-chroma": {
      "command": "python",
      "args": ["-m", "mcp_pdf_chroma.server"],
      "cwd": "/path/to/mcp_pdf_chroma"
    }
  }
}
```

## Available Tools

### 1. load_pdf

Load a PDF from a URL and insert into ChromaDB.

**Parameters:**
- `url` (required): URL of the PDF file
- `filename` (optional): Custom name for the document

**Example:**
```json
{
  "url": "https://arxiv.org/pdf/2301.12345.pdf",
  "filename": "attention_paper"
}
```

**Returns:**
```json
{
  "filename": "attention_paper",
  "source_url": "https://arxiv.org/pdf/2301.12345.pdf",
  "filesize": 2458624,
  "filesize_mb": "2.34 MB",
  "total_pages": 42,
  "total_chunks": 156,
  "created_at": "2024-01-15T10:30:00.000Z",
  "status": "success",
  "message": "Successfully loaded 'attention_paper' with 156 chunks from 42 pages"
}
```

### 2. search_text

Search for text in the vector database.

**Parameters:**
- `query` (required): Search query/question
- `top_k` (required): Number of results to return
- `filename` (optional): Filter by document filename

**Example:**
```json
{
  "query": "What is the attention mechanism?",
  "top_k": 5,
  "filename": "attention_paper"
}
```

**Returns:**
```json
{
  "query": "What is the attention mechanism?",
  "top_k": 5,
  "filename_filter": "attention_paper",
  "count": 5,
  "results": [
    {
      "text": "The attention mechanism allows...",
      "filename": "attention_paper",
      "page_number": 3,
      "chunk_index": 12,
      "similarity_score": 0.8542,
      "source_url": "https://arxiv.org/pdf/2301.12345.pdf"
    }
  ]
}
```

### 3. get_metadata

Retrieve metadata for a loaded document.

**Parameters:**
- `filename` (required): Name of the document

**Example:**
```json
{
  "filename": "attention_paper"
}
```

**Returns:**
```json
{
  "filename": "attention_paper",
  "source_url": "https://arxiv.org/pdf/2301.12345.pdf",
  "filesize": 2458624,
  "filesize_mb": "2.34 MB",
  "total_pages": 42,
  "total_chunks": 156,
  "created_at": "2024-01-15T10:30:00.000Z",
  "last_accessed": "2024-01-15T11:45:00.000Z",
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

### 4. give_page

Get full text of a specific page.

**Parameters:**
- `filename` (required): Name of the document
- `page_number` (required): Page number (1-indexed)

**Example:**
```json
{
  "filename": "attention_paper",
  "page_number": 5
}
```

**Returns:**
```json
{
  "filename": "attention_paper",
  "page_number": 5,
  "total_pages": 42,
  "text": "Full text content of page 5..."
}
```

## Architecture

```
mcp_pdf_chroma/
├── src/
│   └── mcp_pdf_chroma/
│       ├── __init__.py
│       ├── server.py          # Main MCP server
│       ├── config.py           # Configuration management
│       ├── metadata_store.py   # In-memory metadata storage
│       ├── pdf_processor.py    # PDF downloading and processing
│       └── vector_db.py        # ChromaDB integration
├── pyproject.toml
├── requirements.txt
├── call_log.txt               # Automatic call logging (created at runtime)
└── README.md
```

## Call Logging

The server automatically logs all actions to `call_log.txt`. This includes:

### Logged Actions

1. **PDF Loading** - Logs complete metadata when a PDF is processed:
   ```
   [2025-12-14T18:15:31.472759Z] LOAD_PDF
   {
     "url": "https://example.com/document.pdf",
     "filename": "my_document",
     "metadata": {
       "filesize": 2458624,
       "filesize_mb": "2.34 MB",
       "total_pages": 42,
       "total_chunks": 156,
       "created_at": "2025-12-14T18:15:31.472041Z",
       "status": "success"
     }
   }
   ```

2. **Search Queries** - Logs all search requests from agents:
   ```
   [2025-12-14T18:15:31.563683Z] SEARCH_TEXT
   {
     "query": "What is the attention mechanism?",
     "top_k": 5,
     "filename_filter": "attention_paper",
     "results_count": 5
   }
   ```

### Log File Location

The log file is created in the working directory where the server is started:
- **Default**: `./call_log.txt`
- **Format**: Timestamped JSON entries
- **Rotation**: Manual (file grows indefinitely)

### Monitoring Usage

You can monitor the log in real-time:

```bash
# Watch the log file
tail -f call_log.txt

# View recent entries
tail -n 50 call_log.txt

# Search for specific queries
grep "SEARCH_TEXT" call_log.txt
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

### Type Checking

```bash
mypy src/
```

## Dependencies

- **mcp**: Model Context Protocol SDK
- **langchain**: PDF loading and text processing
- **chromadb**: Vector database
- **sentence-transformers**: Local embeddings
- **pypdf**: PDF parsing
- **requests**: HTTP downloads

## Performance

- **Embedding Speed**: ~100-500 chunks/second (hardware dependent)
- **Search Speed**: Sub-second for collections up to 100K chunks
- **Storage**: ~1KB per chunk (text + embedding + metadata)

## Troubleshooting

### Large PDFs

If you encounter memory issues with large PDFs:
1. Reduce `CHUNK_SIZE` in configuration
2. Increase `MAX_PDF_SIZE_MB` if needed
3. Process PDFs in smaller batches

### Embedding Model Download

On first run, the embedding model will be downloaded (~80MB for all-MiniLM-L6-v2). Ensure you have internet connectivity.

### ChromaDB Persistence

ChromaDB data is stored in `CHROMA_DB_PATH`. To reset the database, delete this directory.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
