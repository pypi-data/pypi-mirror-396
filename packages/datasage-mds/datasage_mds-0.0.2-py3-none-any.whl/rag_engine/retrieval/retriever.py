from typing import List, Tuple
import json
import urllib.request
import urllib.error
from .data_models import Document
from ..indexing.vector_store import VectorStore

class RetrievalError(Exception):
    """
    Custom exception for retrieval errors.
    """
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error

class OllamaEmbedder:
    """
    A simple Ollama embedder to embed documents and queries.
    """
    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def _get_embedding(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.model,
            "prompt": text
        }
        data = json.dumps(payload).encode("utf-8")
        
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise RetrievalError(f"Ollama API returned status {response.status}")
                result = json.loads(response.read().decode("utf-8"))
                return result.get("embedding", [])
        except urllib.error.URLError as e:
            raise RetrievalError(f"Failed to connect to Ollama at {self.base_url}: {e}", original_error=e)
        except Exception as e:
            raise RetrievalError(f"An unexpected error occurred during embedding: {e}", original_error=e)

    def embed_query(self, text: str) -> List[float]:
        try:
            return self._get_embedding(text)
        except Exception as e:
            raise RetrievalError(f"Error embedding query: {e}", original_error=e)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return [self._get_embedding(text) for text in texts]
        except Exception as e:
            raise RetrievalError(f"Error embedding documents: {e}", original_error=e)

class Retriever:
    """
    A simple retriever to retrieve documents from a vector store.
    """
    def __init__(self, vector_store: VectorStore, embedder: OllamaEmbedder):
        self.vs = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, k: int = 5, filter: dict = None) -> List[Document]:
        """
        Retrieve documents based on a query.
        """
        try:
            embedding = self.embedder.embed_query(query)
            results = self.vs.store.similarity_search_by_vector(embedding, k=k, filter=filter)
            return [Document(page_content=d.page_content, metadata=d.metadata) for d in results]
        except Exception as e:
            raise RetrievalError(f"Failed to retrieve documents: {e}", original_error=e)

    def retrieve_with_scores(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """
        Retrieve documents along with their similarity scores.
        """
        try:
            # Chroma returns (doc, score) tuples when using similarity_search_with_score
            results = self.vs.store.similarity_search_with_score(query, k=k)
            
            output = []
            for doc, score in results:
                new_doc = Document(page_content=doc.page_content, metadata=doc.metadata)
                output.append((new_doc, score))
            return output
        except Exception as e:
            raise RetrievalError(f"Failed to retrieve documents with scores: {e}", original_error=e)

    def retrieve_by_source(self, query: str, source: str, k: int = 5) -> List[Document]:
        """
        Retrieve documents filtered by a specific source file.
        """
        try:
            return self.retrieve(query, k=k, filter={"source": source})
        except Exception as e:
            raise RetrievalError(f"Failed to retrieve documents by source: {e}", original_error=e)
