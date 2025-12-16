"""
Enhanced Vector Store with custom metadata indexing and analytics.
This module provides intelligent vector storage with additional tracking capabilities.
"""

from typing import List, Dict, Optional, Set
from langchain_core.documents import Document
from langchain_chroma import Chroma
from datetime import datetime
import os


class VectorStore:
    """
    Enhanced vector store with metadata indexing and statistics.
    
    Features:
    - Custom metadata tracking and indexing
    - Document provenance tracking
    - Search analytics
    - Source-based filtering
    """
    
    def __init__(self, embedding_model, persist_dir: str = None):
        """
        Initialize vector store with custom tracking.
        
        Args:
            embedding_model: Embedding function for the vector store
            persist_dir: Directory for persistent storage
        """
        self.store = Chroma(
            embedding_function=embedding_model,
            persist_directory=persist_dir,
            collection_name="datasage"
        )
        self.persist_dir = persist_dir
        
        # Custom document tracking
        self._doc_count = 0
        self._metadata_index: Dict[str, Dict] = {}
        self._source_index: Dict[str, List[str]] = {}
        
        # Search analytics
        self._search_stats = {
            "total_searches": 0,
            "total_results_returned": 0,
            "unique_queries": set(),
            "popular_sources": {}
        }
    
    def add_documents(self, docs: List[Document]) -> List[str]:
        """
        Add documents with custom metadata tracking.
        
        Custom features:
        - Assigns unique document IDs
        - Tracks document provenance
        - Indexes by source for fast filtering
        - Records timestamp of addition
        
        Args:
            docs: List of Document objects to add
            
        Returns:
            List of assigned document IDs
        """
        doc_ids = []
        
        for doc in docs:
            # Assign unique document ID
            doc_id = f"doc_{self._doc_count:06d}"
            doc_ids.append(doc_id)
            
            # Extract source from metadata - handle both old and new format
            # New format uses "path", old format uses "source"
            source = doc.metadata.get("path") or doc.metadata.get("source", "unknown")
            
            # Custom metadata tracking
            self._metadata_index[doc_id] = {
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "content_length": len(doc.page_content),
                "original_metadata": doc.metadata.copy()
            }
            
            # Index by source for fast lookups
            if source not in self._source_index:
                self._source_index[source] = []
            self._source_index[source].append(doc_id)
            
            # Add doc_id to document metadata
            doc.metadata["doc_id"] = doc_id
            doc.metadata["indexed_at"] = datetime.now().isoformat()
            
            self._doc_count += 1
        
        # Add to vector store
        self.store.add_documents(docs)
        
        print(f"Added {len(docs)} documents (IDs: {doc_ids[0]} to {doc_ids[-1]})")
        
        return doc_ids
    
    def search(self, query: str, k: int = 5, filter: dict = None) -> List[Document]:
        """
        Search with custom analytics and relevance scoring.
        
        Custom features:
        - Tracks search queries for analytics
        - Adds rank and relevance metadata
        - Updates source popularity metrics
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of relevant Document objects with enhanced metadata
        """
        # Update search statistics
        self._search_stats["total_searches"] += 1
        self._search_stats["unique_queries"].add(query)
        
        # Perform similarity search
        results = self.store.similarity_search(query, k=k, filter=filter)
        
        # Update statistics
        self._search_stats["total_results_returned"] += len(results)
        
        # Enhance results with custom metadata
        for i, doc in enumerate(results):
            # Add ranking information
            doc.metadata["search_rank"] = i + 1
            doc.metadata["relevance_score"] = 1.0 / (i + 1)  # Simple inverse rank
            
            # Track source popularity - handle both old and new format
            source = doc.metadata.get("path") or doc.metadata.get("source", "unknown")
            self._search_stats["popular_sources"][source] = (
                self._search_stats["popular_sources"].get(source, 0) + 1
            )
        
        return results
    
    def search_by_source(self, query: str, source: str, k: int = 5) -> List[Document]:
        """
        Custom search within a specific source.
        
        This uses the source index for efficient filtering.
        
        Args:
            query: Search query
            source: Source to filter by
            k: Number of results
            
        Returns:
            Documents from the specified source
        """
        # Try filtering by both "path" and "source" for compatibility
        filter_dict = {"path": source}
        return self.search(query, k=k, filter=filter_dict)
    
    def get_sources(self) -> List[str]:
        """
        Get list of all unique sources in the vector store.
        
        Returns:
            List of source identifiers
        """
        return list(self._source_index.keys())
    
    def get_document_count_by_source(self, source: str) -> int:
        """
        Get number of documents from a specific source.
        
        Args:
            source: Source identifier
            
        Returns:
            Number of documents from that source
        """
        return len(self._source_index.get(source, []))
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive vector store statistics.
        
        Custom analytics including:
        - Document counts
        - Source distribution
        - Search patterns
        - Storage information
        
        Returns:
            Dictionary of statistics
        """
        # Calculate src distribution
        source_distribution = {
            source: len(doc_ids) 
            for source, doc_ids in self._source_index.items()
        }
        
        # Get most popular sources from searches
        top_sources = sorted(
            self._search_stats["popular_sources"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Calculate average content length
        total_length = sum(
            meta["content_length"] 
            for meta in self._metadata_index.values()
        )
        avg_length = total_length / max(self._doc_count, 1)
        
        return {
            "total_documents": self._doc_count,
            "unique_sources": len(self._source_index),
            "source_distribution": source_distribution,
            "total_searches": self._search_stats["total_searches"],
            "unique_queries": len(self._search_stats["unique_queries"]),
            "avg_results_per_search": (
                self._search_stats["total_results_returned"] / 
                max(self._search_stats["total_searches"], 1)
            ),
            "top_searched_sources": dict(top_sources),
            "avg_document_length": f"{avg_length:.0f} characters",
            "persist_directory": self.persist_dir or "in-memory"
        }
    
    def get_document_info(self, doc_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document metadata or None if not found
        """
        return self._metadata_index.get(doc_id)
    
    def list_documents_by_source(self, source: str) -> List[str]:
        """
        List all document IDs from a specific source.
        
        Args:
            source: Source identifier
            
        Returns:
            List of document IDs
        """
        return self._source_index.get(source, []).copy()