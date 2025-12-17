"""MCP Server implementation for PDF processing and semantic search."""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

from . import config
from .metadata_store import MetadataStore, DocumentMetadata
from .pdf_processor import PDFProcessor
from .vector_db import ChromaDBManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Call log file path
CALL_LOG_FILE = Path("call_log.txt")


class PDFChromaServer:
    """MCP Server for PDF processing with semantic search via ChromaDB."""
    
    def __init__(self):
        """Initialize the server."""
        self.server = Server("pdf-chroma-server")
        
        # Initialize components
        logger.info("Initializing PDF ChromaDB Server...")
        self.metadata_store = MetadataStore(config.METADATA_PERSISTENCE_FILE)
        self.pdf_processor = PDFProcessor()
        self.vector_db = ChromaDBManager()
        
        # Initialize call log file
        self._init_call_log()
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Server initialization complete")
    
    def _init_call_log(self):
        """Initialize the call log file."""
        if not CALL_LOG_FILE.exists():
            with open(CALL_LOG_FILE, 'w') as f:
                f.write(f"=== MCP PDF ChromaDB Server - Call Log ===\n")
                f.write(f"Started: {datetime.utcnow().isoformat()}Z\n")
                f.write("=" * 60 + "\n\n")
    
    def _log_call(self, action: str, details: Dict[str, Any]):
        """Log a call to the call log file.
        
        Args:
            action: Type of action (e.g., 'LOAD_PDF', 'SEARCH_TEXT')
            details: Dictionary with action details
        """
        try:
            with open(CALL_LOG_FILE, 'a') as f:
                timestamp = datetime.utcnow().isoformat() + "Z"
                f.write(f"\n[{timestamp}] {action}\n")
                f.write(json.dumps(details, indent=2))
                f.write("\n" + "-" * 60 + "\n")
        except Exception as e:
            logger.error(f"Failed to write to call log: {e}")
    
    def _register_handlers(self):
        """Register MCP server handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="load_pdf",
                    description="Load a PDF from URL, chunk it, and insert into ChromaDB with metadata for later search",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL of the PDF file to load"
                            },
                            "filename": {
                                "type": "string",
                                "description": "Custom name for the document (optional, extracted from URL if not provided)"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="search_text",
                    description="Search for related content in the vector database and return relevant fragments (RAG)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query/question"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 5
                            },
                            "filename": {
                                "type": "string",
                                "description": "Filter results by document filename (optional)"
                            }
                        },
                        "required": ["query", "top_k"]
                    }
                ),
                Tool(
                    name="get_metadata",
                    description="Retrieve stored metadata for a loaded document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the document"
                            }
                        },
                        "required": ["filename"]
                    }
                ),
                Tool(
                    name="give_page",
                    description="Get the full text content of a specific page from a PDF",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the document"
                            },
                            "page_number": {
                                "type": "integer",
                                "description": "Page number to extract (1-indexed)"
                            }
                        },
                        "required": ["filename", "page_number"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "load_pdf":
                    result = await self._load_pdf(arguments)
                elif name == "search_text":
                    result = await self._search_text(arguments)
                elif name == "get_metadata":
                    result = await self._get_metadata(arguments)
                elif name == "give_page":
                    result = await self._give_page(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=str(result))]
            
            except Exception as e:
                logger.error(f"Error in {name}: {e}", exc_info=True)
                error_result = {
                    "status": "error",
                    "error": str(e)
                }
                return [TextContent(type="text", text=str(error_result))]
    
    async def _load_pdf(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Load PDF and insert into ChromaDB.
        
        Args:
            args: Dictionary with 'url' and optional 'filename'
            
        Returns:
            Document metadata
        """
        url = args['url']
        filename = args.get('filename')
        
        # Extract filename from URL if not provided
        if not filename:
            filename = PDFProcessor.extract_filename_from_url(url)
        
        logger.info(f"Loading PDF: {filename} from {url}")
        
        # Download PDF
        file_path, file_size = self.pdf_processor.download_pdf(url, filename)
        
        # Load and chunk PDF
        chunks, total_pages = self.pdf_processor.load_and_chunk_pdf(file_path, filename)
        
        # Add to vector database
        total_chunks = self.vector_db.add_documents(chunks, url)
        
        # Create metadata
        created_at = datetime.utcnow().isoformat() + "Z"
        metadata = DocumentMetadata(
            filename=filename,
            source_url=url,
            filesize=file_size,
            filesize_mb=f"{file_size / 1024 / 1024:.2f} MB",
            total_pages=total_pages,
            total_chunks=total_chunks,
            created_at=created_at,
            last_accessed=created_at,
            chunk_size=self.pdf_processor.chunk_size,
            chunk_overlap=self.pdf_processor.chunk_overlap,
            pdf_cache_path=str(file_path)
        )
        
        # Store metadata
        self.metadata_store.add(metadata)
        
        # Prepare result
        result = {
            "filename": filename,
            "source_url": url,
            "filesize": file_size,
            "filesize_mb": metadata.filesize_mb,
            "total_pages": total_pages,
            "total_chunks": total_chunks,
            "created_at": created_at,
            "status": "success",
            "message": f"Successfully loaded '{filename}' with {total_chunks} chunks from {total_pages} pages"
        }
        
        # Log the action
        self._log_call("LOAD_PDF", {
            "url": url,
            "filename": filename,
            "metadata": result
        })
        
        return result
    
    async def _search_text(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for text in vector database.
        
        Args:
            args: Dictionary with 'query', 'top_k', and optional 'filename'
            
        Returns:
            Search results
        """
        query = args['query']
        top_k = args['top_k']
        filename = args.get('filename')
        
        # Perform search
        results = self.vector_db.search(query, top_k, filename)
        
        result = {
            "query": query,
            "top_k": top_k,
            "filename_filter": filename,
            "results": results,
            "count": len(results)
        }
        
        # Log the query
        self._log_call("SEARCH_TEXT", {
            "query": query,
            "top_k": top_k,
            "filename_filter": filename,
            "results_count": len(results)
        })
        
        return result
    
    async def _get_metadata(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata for a document.
        
        Args:
            args: Dictionary with 'filename'
            
        Returns:
            Document metadata
        """
        filename = args['filename']
        
        metadata = self.metadata_store.get(filename)
        
        if not metadata:
            raise ValueError(f"Document '{filename}' not found in metadata store")
        
        return {
            "filename": metadata.filename,
            "source_url": metadata.source_url,
            "filesize": metadata.filesize,
            "filesize_mb": metadata.filesize_mb,
            "total_pages": metadata.total_pages,
            "total_chunks": metadata.total_chunks,
            "created_at": metadata.created_at,
            "last_accessed": metadata.last_accessed,
            "chunk_size": metadata.chunk_size,
            "chunk_overlap": metadata.chunk_overlap
        }
    
    async def _give_page(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get page text from PDF.
        
        Args:
            args: Dictionary with 'filename' and 'page_number'
            
        Returns:
            Page content
        """
        filename = args['filename']
        page_number = args['page_number']
        
        # Get metadata to find cached file
        metadata = self.metadata_store.get(filename)
        
        if not metadata:
            raise ValueError(f"Document '{filename}' not found")
        
        # Get page text
        file_path = Path(metadata.pdf_cache_path)
        
        if not file_path.exists():
            raise ValueError(f"Cached PDF file not found: {file_path}")
        
        page_text = self.pdf_processor.get_page_text(file_path, page_number)
        
        return {
            "filename": filename,
            "page_number": page_number,
            "total_pages": metadata.total_pages,
            "text": page_text
        }
    
    async def run(self):
        """Run the server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Server running on stdio")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point."""
    server = PDFChromaServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
