"""ChromaDB vector database integration with local embeddings."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document

from . import config

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """Manage ChromaDB collection with local embeddings."""
    
    def __init__(self, collection_name: str = "pdf_documents"):
        """Initialize ChromaDB manager.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB at: {config.CHROMA_DB_PATH}")
        self.client = chromadb.PersistentClient(
            path=str(config.CHROMA_DB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "PDF document chunks with embeddings"}
        )
        
        logger.info(f"ChromaDB collection '{collection_name}' ready")
    
    def add_documents(self, documents: List[Document], source_url: str) -> int:
        """Add document chunks to ChromaDB.
        
        Args:
            documents: List of LangChain Document chunks
            source_url: Original URL of the PDF
            
        Returns:
            Number of chunks added
        """
        if not documents:
            return 0
        
        logger.info(f"Adding {len(documents)} chunks to ChromaDB")
        
        # Prepare data
        ids = []
        texts = []
        metadatas = []
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        for i, doc in enumerate(documents):
            # Create unique ID
            filename = doc.metadata.get('filename', 'unknown')
            chunk_idx = doc.metadata.get('chunk_index', i)
            doc_id = f"{filename}_{chunk_idx}"
            
            ids.append(doc_id)
            texts.append(doc.page_content)
            
            # Prepare metadata
            metadata = {
                'filename': filename,
                'page_number': doc.metadata.get('page_number', 0),
                'chunk_index': chunk_idx,
                'source_url': source_url,
                'total_pages': doc.metadata.get('total_pages', 0),
                'created_at': timestamp
            }
            metadatas.append(metadata)
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully added {len(documents)} chunks")
        return len(documents)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filename: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filename: Optional filter by filename
            
        Returns:
            List of search results with text, metadata, and scores
        """
        logger.info(f"Searching for: '{query}' (top_k={top_k}, filename={filename})")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True
        ).tolist()
        
        # Prepare filter
        where_filter = None
        if filename:
            where_filter = {"filename": filename}
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                # Convert distance to similarity score (0-1)
                # ChromaDB uses L2 distance, convert to similarity
                distance = results['distances'][0][i]
                similarity = 1 / (1 + distance)
                
                result = {
                    'text': results['documents'][0][i],
                    'filename': results['metadatas'][0][i]['filename'],
                    'page_number': results['metadatas'][0][i]['page_number'],
                    'chunk_index': results['metadatas'][0][i]['chunk_index'],
                    'similarity_score': round(similarity, 4),
                    'source_url': results['metadatas'][0][i]['source_url']
                }
                formatted_results.append(result)
        
        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results
    
    def document_exists(self, filename: str) -> bool:
        """Check if document exists in collection.
        
        Args:
            filename: Name of the document
            
        Returns:
            True if document has chunks in collection
        """
        results = self.collection.get(
            where={"filename": filename},
            limit=1
        )
        return len(results['ids']) > 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics.
        
        Returns:
            Dictionary with collection stats
        """
        count = self.collection.count()
        return {
            'total_chunks': count,
            'collection_name': self.collection_name
        }
