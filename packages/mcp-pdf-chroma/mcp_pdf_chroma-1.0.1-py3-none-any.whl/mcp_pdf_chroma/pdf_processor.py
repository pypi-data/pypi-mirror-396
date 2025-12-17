"""PDF processing utilities using LangChain."""

import logging
import requests
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse
import hashlib

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from . import config

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handle PDF downloading, loading, and chunking."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """Initialize PDF processor.
        
        Args:
            chunk_size: Size of text chunks (default from config)
            chunk_overlap: Overlap between chunks (default from config)
        """
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def download_pdf(self, url: str, filename: str) -> Tuple[Path, int]:
        """Download PDF from URL.
        
        Args:
            url: URL of the PDF file
            filename: Name to save the file as
            
        Returns:
            Tuple of (file_path, file_size_bytes)
            
        Raises:
            ValueError: If URL is invalid or file too large
            requests.RequestException: If download fails
        """
        # Validate URL
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError(f"Invalid URL: {url}")
        
        # Create safe filename
        safe_filename = self._sanitize_filename(filename)
        if not safe_filename.endswith('.pdf'):
            safe_filename += '.pdf'
        
        file_path = config.PDF_CACHE_DIR / safe_filename
        
        logger.info(f"Downloading PDF from {url}")
        
        # Download with streaming to check size
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Check file size
        content_length = response.headers.get('content-length')
        if content_length:
            size = int(content_length)
            if size > config.MAX_PDF_SIZE_BYTES:
                raise ValueError(
                    f"PDF size ({size / 1024 / 1024:.2f} MB) exceeds "
                    f"maximum allowed size ({config.MAX_PDF_SIZE_MB} MB)"
                )
        
        # Download file
        with open(file_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Check size during download
                    if downloaded > config.MAX_PDF_SIZE_BYTES:
                        file_path.unlink()  # Delete partial file
                        raise ValueError(
                            f"PDF exceeds maximum allowed size ({config.MAX_PDF_SIZE_MB} MB)"
                        )
        
        file_size = file_path.stat().st_size
        logger.info(f"Downloaded PDF: {file_path} ({file_size / 1024 / 1024:.2f} MB)")
        
        return file_path, file_size
    
    def load_and_chunk_pdf(self, file_path: Path, filename: str) -> Tuple[List[Document], int]:
        """Load PDF and split into chunks.
        
        Args:
            file_path: Path to the PDF file
            filename: Document filename for metadata
            
        Returns:
            Tuple of (list of Document chunks, total_pages)
        """
        logger.info(f"Loading PDF: {file_path}")
        
        # Load PDF with page numbers
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        
        total_pages = len(pages)
        logger.info(f"Loaded {total_pages} pages from PDF")
        
        # Split into chunks while preserving page numbers
        all_chunks = []
        chunk_index = 0
        
        for page in pages:
            # Split page content
            page_chunks = self.text_splitter.split_documents([page])
            
            # Add metadata to each chunk
            for chunk in page_chunks:
                chunk.metadata.update({
                    'filename': filename,
                    'page_number': page.metadata.get('page', 0) + 1,  # 1-indexed
                    'chunk_index': chunk_index,
                    'total_pages': total_pages
                })
                chunk_index += 1
                all_chunks.append(chunk)
        
        logger.info(f"Created {len(all_chunks)} chunks from {total_pages} pages")
        
        return all_chunks, total_pages
    
    def get_page_text(self, file_path: Path, page_number: int) -> str:
        """Extract text from a specific page.
        
        Args:
            file_path: Path to the PDF file
            page_number: Page number (1-indexed)
            
        Returns:
            Text content of the page
            
        Raises:
            ValueError: If page number is invalid
        """
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        
        if page_number < 1 or page_number > len(pages):
            raise ValueError(
                f"Invalid page number {page_number}. "
                f"Document has {len(pages)} pages."
            )
        
        # Get page (convert to 0-indexed)
        page = pages[page_number - 1]
        return page.page_content
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Create safe filename.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove unsafe characters
        safe = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
        safe = safe.strip().replace(' ', '_')
        
        # Limit length
        if len(safe) > 200:
            safe = safe[:200]
        
        return safe or "document"
    
    @staticmethod
    def extract_filename_from_url(url: str) -> str:
        """Extract filename from URL.
        
        Args:
            url: URL string
            
        Returns:
            Extracted filename or hash-based filename
        """
        parsed = urlparse(url)
        path = Path(parsed.path)
        
        if path.name and path.suffix == '.pdf':
            return path.stem
        
        # Generate filename from URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"document_{url_hash}"
