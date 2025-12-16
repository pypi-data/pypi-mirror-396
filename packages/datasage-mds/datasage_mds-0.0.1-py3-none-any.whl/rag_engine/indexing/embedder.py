"""
Embedder with text preprocessing.
"""

from typing import List
from langchain_huggingface import HuggingFaceEmbeddings


class Embedder:
    """
    Text embedder with preprocessing.
    
    Features:
    - Text preprocessing for consistency
    - Batch processing with progress updates
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedder.
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.model = HuggingFaceEmbeddings(model_name=model_name)
        self.model_name = model_name
    
    def _preprocess_text(self, text: str) -> str:
        """
        Custom preprocessing pipeline for text normalization.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Remove extra whitespace
        text = " ".join(text.split())
        # Strip leading/trailing spaces
        text = text.strip()
        return text
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query with preprocessing.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Generate embedding
        embedding = self.model.embed_query(processed_text)
        
        return embedding
    
    def embed_documents(self, texts: List[str], show_progress: bool = False) -> List[List[float]]:
        """
        Embed multiple documents with optional progress tracking.
        
        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress updates
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            # Show progress for large batches
            if show_progress and (i + 1) % 10 == 0:
                print(f"Embedding progress: {i + 1}/{len(texts)} documents")
            
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        
        if show_progress:
            print(f"Batch complete: {len(texts)} documents embedded")
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension size
        """
        test_embedding = self.embed_query("test")
        return len(test_embedding)