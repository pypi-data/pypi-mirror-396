"""Metadata storage management for documents."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Document metadata structure."""
    filename: str
    source_url: str
    filesize: int
    filesize_mb: str
    total_pages: int
    total_chunks: int
    created_at: str
    last_accessed: str
    chunk_size: int
    chunk_overlap: int
    pdf_cache_path: str


class MetadataStore:
    """In-memory metadata storage with optional persistence."""
    
    def __init__(self, persistence_file: Optional[Path] = None):
        """Initialize metadata store.
        
        Args:
            persistence_file: Optional path to JSON file for persistence
        """
        self.persistence_file = persistence_file
        self._store: Dict[str, DocumentMetadata] = {}
        
        # Load existing metadata if available
        if persistence_file and persistence_file.exists():
            self._load_from_file()
    
    def add(self, metadata: DocumentMetadata) -> None:
        """Add or update document metadata.
        
        Args:
            metadata: Document metadata to store
        """
        self._store[metadata.filename] = metadata
        self._save_to_file()
        logger.info(f"Added metadata for document: {metadata.filename}")
    
    def get(self, filename: str) -> Optional[DocumentMetadata]:
        """Retrieve document metadata.
        
        Args:
            filename: Name of the document
            
        Returns:
            Document metadata or None if not found
        """
        metadata = self._store.get(filename)
        if metadata:
            # Update last accessed time
            metadata.last_accessed = datetime.utcnow().isoformat() + "Z"
            self._save_to_file()
        return metadata
    
    def exists(self, filename: str) -> bool:
        """Check if document metadata exists.
        
        Args:
            filename: Name of the document
            
        Returns:
            True if metadata exists
        """
        return filename in self._store
    
    def list_all(self) -> Dict[str, DocumentMetadata]:
        """Get all stored metadata.
        
        Returns:
            Dictionary of all document metadata
        """
        return self._store.copy()
    
    def _save_to_file(self) -> None:
        """Save metadata to persistence file."""
        if not self.persistence_file:
            return
        
        try:
            data = {
                filename: asdict(metadata) 
                for filename, metadata in self._store.items()
            }
            with open(self.persistence_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved metadata to {self.persistence_file}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _load_from_file(self) -> None:
        """Load metadata from persistence file."""
        try:
            with open(self.persistence_file, 'r') as f:
                data = json.load(f)
            
            self._store = {
                filename: DocumentMetadata(**metadata)
                for filename, metadata in data.items()
            }
            logger.info(f"Loaded {len(self._store)} documents from {self.persistence_file}")
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            self._store = {}
