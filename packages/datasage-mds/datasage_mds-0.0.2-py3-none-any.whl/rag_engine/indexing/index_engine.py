"""
Enhanced Indexing Engine with validation, progress tracking, and orchestration.
This module coordinates the complete indexing pipeline.
"""

import os
from typing import List, Optional, Dict, Set
from langchain_core.documents import Document
from datetime import datetime
import logging


from ..ingestion.chunker import TextChunker
from ..ingestion.loaders import (
    DocumentLoader,
    PDFLoader,
    CSVLoader,
    TXTLoader
)
from .embedder import Embedder
from .vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User-defined Exceptions
class IndexingException(Exception):
    """Base exception for indexing operations."""
    pass


class FileValidationError(IndexingException):
    """Raised when file validation fails."""
    pass

class LoaderError(IndexingException):
    """Raised when document loading fails."""
    pass

class ChunkingError(IndexingException):
    """Raised when document chunking fails."""
    pass

class StorageError(IndexingException):
    """Raised when vector store operations fail."""
    pass
    


class IndexingEngine:
    """
    High-level indexing pipeline with validation and tracking.
    
    Custom orchestration features:
    - File validation and duplicate detection
    - Progress tracking and logging
    - Multi-file batch indexing
    - System-wide statistics aggregation
    - Error handling and recovery
    """

    def __init__(
        self,
        persist_dir: Optional[str] = "./datasage_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        overlap: int = 200,
    ):
        """
        Initialize indexing engine with custom tracking.
        
        Args:
            persist_dir: Directory for vector database persistence
            embedding_model: HuggingFace embedding model name
            chunk_size: Maximum characters per chunk
            overlap: Overlapping characters between chunks
        """
        self.chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)
        self.embedder = Embedder(model_name=embedding_model)
        self.vector_store = VectorStore(
            embedding_model=self.embedder.model,
            persist_dir=persist_dir,
        )
        
        self.persist_dir = persist_dir
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        self._indexed_files: Set[str] = set()
        self._failed_files: Dict[str, str] = {}
        self._indexing_history: List[Dict] = []
        self._supported_extensions = {'.pdf', '.csv', '.txt'}
    
    def _validate_file(self, file_path: str) -> None:
        """
        Custom file validation with detailed error messages.
        
        Validates:
        - File existence
        - File readability
        - Supported file type
        - Non-empty file
        
        Args:
            file_path: Path to file to validate
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError(f"File is empty: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self._supported_extensions:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                f"Supported types: {', '.join(self._supported_extensions)}"
            )
        
        # Check read permissions
        if not os.access(file_path, os.R_OK):
            raise ValueError(f"File is not readable: {file_path}")
    
    def _get_loader(self, file_path: str) -> DocumentLoader:
        """
        Select appropriate loader based on file extension.
        
        Custom loader selection with error handling.
        
        Args:
            file_path: Path to file
            
        Returns:
            Appropriate DocumentLoader instance
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        loader_map = {
            '.pdf': PDFLoader,
            '.csv': CSVLoader,
            '.txt': TXTLoader
        }
        
        loader_class = loader_map.get(ext)
        if not loader_class:
            raise ValueError(f"No loader available for extension: {ext}")
        
        return loader_class()
    
    def _check_duplicate(self, file_path: str) -> bool:
        """
        Check if file has already been indexed.
        
        Custom duplicate detection.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file was already indexed
        """
        # Normalize path for comparison
        normalized_path = os.path.abspath(file_path)
        return normalized_path in self._indexed_files
    
    def index(
        self, 
        file_path: str, 
        metadata: Optional[dict] = None,
        force_reindex: bool = False,
        verbose: bool = True
    ) -> List[Document]:
        """
        Index a file with validation, progress tracking, and error handling.
        
        Custom orchestration features:
        - Pre-validation
        - Duplicate detection
        - Progress logging
        - Error recovery
        - History tracking
        
        Args:
            file_path: Path to file to index
            metadata: Additional metadata to attach
            force_reindex: Re-index even if already processed
            verbose: Print progress messages
            
        Returns:
            List of created document chunks
        """
        start_time = datetime.now()
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Starting indexing: {file_path}")
            print(f"{'='*60}")
        
        try:
            # Step 1: Validate file
            if verbose:
                print("Step 1: Validating file...")
            self._validate_file(file_path)
            if verbose:
                print(f"File validation passed")
            
            # Step 2: Check for duplicates
            normalized_path = os.path.abspath(file_path)
            if self._check_duplicate(file_path) and not force_reindex:
                if verbose:
                    print(f"Warning: File already indexed. Use force_reindex=True to re-index.")
                return []
            
            # Step 3: Load documents
            if verbose:
                print("Step 2: Loading documents...")
            loader = self._get_loader(file_path)
            if verbose:
                print(f"Using loader: {loader.__class__.__name__}")
            
            # New loaders take a LIST of paths
            docs = loader.load([file_path])
            if verbose:
                print(f"Loaded {len(docs)} document(s)")
            
            # Step 4: Apply custom metadata
            if metadata:
                if verbose:
                    print("Step 3: Applying custom metadata...")
                for d in docs:
                    d.metadata.update(metadata)
            
            # Step 5: Chunk documents
            if verbose:
                print("Step 4: Chunking documents...")
            # Changed from chunk_documents to chunk_docs
            chunks = self.chunker.chunk_docs(docs)
            if verbose:
                print(f"Created {len(chunks)} chunk(s)")
                print(f"Chunk size: {self.chunk_size} chars")
                print(f"Overlap: {self.overlap} chars")
            
            # Step 6: Store in vector database
            if verbose:
                print("Step 5: Storing in vector database...")
            doc_ids = self.vector_store.add_documents(chunks)
            if verbose:
                print(f"Stored {len(chunks)} chunks in vector database")
            
            # Step 7: Update tracking
            self._indexed_files.add(normalized_path)
            
            # Record in history
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            history_entry = {
                "file_path": file_path,
                "timestamp": start_time.isoformat(),
                "duration_seconds": duration,
                "documents_loaded": len(docs),
                "chunks_created": len(chunks),
                "status": "success"
            }
            self._indexing_history.append(history_entry)
            
            if verbose:
                print(f"\n{'='*60}")
                print(f"✓ Indexing complete!")
                print(f"  Duration: {duration:.2f}s")
                print(f"  Total chunks indexed: {len(chunks)}")
                print(f"{'='*60}\n")
            
            return chunks
            
        except Exception as e:
            # Record failure
            self._failed_files[file_path] = str(e)
            
            history_entry = {
                "file_path": file_path,
                "timestamp": start_time.isoformat(),
                "status": "failed",
                "error": str(e)
            }
            self._indexing_history.append(history_entry)
            
            if verbose:
                print(f"\n✗ Indexing failed: {e}\n")
            
            raise
    
    def batch_index(
        self, 
        file_paths: List[str], 
        metadata: Optional[dict] = None,
        continue_on_error: bool = True,
        verbose: bool = True
    ) -> Dict[str, List[Document]]:
        """
        Index multiple files in batch with error handling.
        
        Custom batch processing:
        - Processes files sequentially
        - Optional error recovery
        - Aggregated progress reporting
        - Summary statistics
        
        Args:
            file_paths: List of file paths to index
            metadata: Metadata to apply to all files
            continue_on_error: Continue if a file fails
            verbose: Print progress
            
        Returns:
            Dictionary mapping file paths to their chunks
        """
        results = {}
        successful = 0
        failed = 0
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Batch indexing {len(file_paths)} file(s)")
            print(f"{'='*60}\n")
        
        for i, file_path in enumerate(file_paths, 1):
            if verbose:
                print(f"[{i}/{len(file_paths)}] Processing: {file_path}")
            
            try:
                chunks = self.index(
                    file_path, 
                    metadata=metadata, 
                    verbose=False
                )
                results[file_path] = chunks
                successful += 1
                
                if verbose:
                    print(f"Success: {len(chunks)} chunks created\n")
                    
            except Exception as e:
                failed += 1
                results[file_path] = []
                
                if verbose:
                    print(f"Failed: {e}\n")
                
                if not continue_on_error:
                    raise
        
        if verbose:
            print(f"{'='*60}")
            print(f"Batch indexing complete!")
            print(f"  Successful: {successful}/{len(file_paths)}")
            print(f"  Failed: {failed}/{len(file_paths)}")
            print(f"{'='*60}\n")
        
        return results
    
    def search(
        self, 
        query: str, 
        k: int = 5, 
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        Search the indexed documents.
        
        Args:
            query: Search query
            k: Number of results
            filter: Optional metadata filter
            
        Returns:
            List of relevant documents
        """
        return self.vector_store.search(query, k=k, filter=filter)
    
    def get_indexed_files(self) -> List[str]:
        """Get list of successfully indexed files."""
        return list(self._indexed_files)
    
    def get_failed_files(self) -> Dict[str, str]:
        """Get dictionary of failed files and their errors."""
        return self._failed_files.copy()
    
    def get_indexing_history(self) -> List[Dict]:
        """Get complete indexing history."""
        return self._indexing_history.copy()
    
    def get_system_statistics(self) -> Dict:
        """
        Get comprehensive system-wide statistics.
        
        Aggregates statistics from all components:
        - Indexing history
        - Chunker settings
        - Vector store analytics
        
        Returns:
            Dictionary of system statistics
        """
        total_chunks = sum(
            entry.get("chunks_created", 0) 
            for entry in self._indexing_history 
            if entry["status"] == "success"
        )
        
        total_duration = sum(
            entry.get("duration_seconds", 0)
            for entry in self._indexing_history
            if entry["status"] == "success"
        )
        
        return {
            "indexing": {
                "files_indexed": len(self._indexed_files),
                "files_failed": len(self._failed_files),
                "total_chunks_created": total_chunks,
                "total_indexing_time": f"{total_duration:.2f}s",
                "avg_time_per_file": (
                    f"{total_duration / max(len(self._indexed_files), 1):.2f}s"
                )
            },
            "configuration": {
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.overlap,
                "persist_directory": self.persist_dir,
                "embedding_model": self.embedder.model_name,
                "embedding_dimension": self.embedder.get_embedding_dimension()
            },
            "vector_store": self.vector_store.get_statistics()
        }
    
    def reset_history(self):
        """Clear indexing history (keeps indexed files)."""
        self._indexing_history.clear()
        self._failed_files.clear()
        print("Indexing history reset")