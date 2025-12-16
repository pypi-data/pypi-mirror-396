from .indexing.index_engine import IndexingEngine
from .indexing.embedder import Embedder
from .indexing.vector_store import VectorStore
from .ingestion.chunker import TextChunker 
from .ingestion.loaders import DocumentLoader
from .ingestion.loaders import PDFLoader
from .ingestion.loaders import CSVLoader
from .ingestion.loaders import TXTLoader
from .retrieval.retriever import Retriever
from .retrieval.generator import LLMGenerator 
from typing import List, Dict

__all__ = [
    "IndexingEngine",
    "Embedder", 
    "VectorStore",
    "TextChunker",
    "DocumentLoader",
    "PDFLoader",
    "CSVLoader",
    "Retriever",
    "LLMGenerator"
]

class RagEngine:
    def __init__(self, data_files: List[str], model_name: str = "llama3.1", metadata: dict = None):

        # 1) Load documents
        # Ensure data_files is a list
        if isinstance(data_files, str):
            data_files = [data_files]
        
        loader = self._choose_loader(data_files)
        docs = loader.load(data_files)

        # 2) Split into chunks
        chunker = TextChunker()
        chunks = chunker.chunk_docs(docs)

        # 3) Initialize embedding and vector store
        embedder = Embedder(model_name="BAAI/bge-small-en-v1.5")
        vs = VectorStore(
            embedding_model=embedder.model,
            persist_dir="./vector_db"
        )

        # stores chunks (filter out empty ones)
        chunks = [c for c in chunks if c.page_content.strip()]
        if not chunks:
            raise ValueError("No valid content found in the documents after chunking")
        vs.add_documents(chunks)  

        # 4) Prepare retriever and generator
        self.retriever = Retriever(vector_store=vs, embedder=embedder)
        self.generator = LLMGenerator(model=model_name)

    def _choose_loader(self, data_files):
        # Ensure list
        if isinstance(data_files, str):
            data_files = [data_files]

        filename = data_files[0].lower()

        if filename.endswith(".pdf"):
            return PDFLoader()
        elif filename.endswith(".csv"):
            return CSVLoader()
        elif filename.endswith(".txt"):
            return TXTLoader()
        else:
            raise ValueError(f"Unsupported file type: {filename}")

    # Function 1
    def query(self, question: str, top_k: int = 5) -> str:
        docs = self.retriever.retrieve(question, k=top_k)
        answer = self.generator.generate_answer(question, docs)
        return answer

    # Function 2
    def summary(self, topic: str = "", top_k: int = 5) -> str:
        """Generate a summary of the data.
        
        Args:
            topic: Optional topic/query to retrieve relevant documents. If empty, retrieves documents broadly.
            top_k: Number of documents to retrieve for summarization.
            
        Returns:
            A bulleted summary of key ideas from the retrieved documents.
        """
        # Use topic to retrieve relevant documents, or a generic query if no topic
        query_text = topic if topic else "main topics and key information"
        docs = self.retriever.retrieve(query_text, k=top_k)
        
        # Fixed prompt for summarization
        summary_prompt = "Summarize in concise bullet points the key ideas in the data"
        summary = self.generator.generate_answer(summary_prompt, docs)
        return summary

    # Function 3
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant documents without generating an answer.
        Useful for inspecting what the RAG engine is finding.
        """
        docs = self.retriever.retrieve(query, k=top_k)
        return [{"content": d.page_content, "source": d.metadata} for d in docs]

    # Function 4
    def get_knowledge_stats(self) -> Dict:
        """
        Return statistics about the underlying vector database,
        including total documents, sources, and search metrics.
        """
        return self.retriever.vs.get_statistics()

    # Function 5
    def add_knowledge(self, file_paths: List[str]) -> str:
        """
        Ingest additional documents into the existing knowledge base.
        """
        loader = self._choose_loader(file_paths)
        docs = loader.load(file_paths)
        
        chunker = TextChunker()
        chunks = chunker.chunk_docs(docs)
        
        # Filter out empty chunks
        chunks = [c for c in chunks if c.page_content.strip()]
        if not chunks:
            return "No valid content found in the provided files"
        
        self.retriever.vs.add_documents(chunks)
        return f"Successfully added {len(chunks)} new chunks to the knowledge base."