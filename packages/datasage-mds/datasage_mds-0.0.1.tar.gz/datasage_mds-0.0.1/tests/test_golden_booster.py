
import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Mock the Document class to fix TypeErrors
class MockDocument:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}
    def __repr__(self):
        return f"Doc({self.page_content})"

class TestGoldenCoverage(unittest.TestCase):
    def test_chunker_golden(self):
        with patch("rag_engine.ingestion.chunker.Document", MockDocument):
            from rag_engine.ingestion.chunker import TextChunker
            c = TextChunker(chunk_size=10, overlap=2)
            
            c.set_size(100) 
            self.assertEqual(c.chunk_size, 100)
            
            doc = MockDocument("HelloWorld"*5, {"source": "test"})
            chunks = c.chunk_docs([doc])
            self.assertTrue(len(chunks) > 0)

    def test_loaders_golden(self):
        with patch("rag_engine.ingestion.loaders.Document", MockDocument):
            from rag_engine.ingestion.loaders import PDFLoader
            
            mock_pdf = MagicMock()
            mock_pdf.pages = [MagicMock(extract_text=lambda: "content")]
            
            with patch.dict(sys.modules, {'pypdf': MagicMock(PdfReader=lambda x: mock_pdf)}):
                l = PDFLoader()
                docs = l.load(["fake.pdf"])
                self.assertEqual(len(docs), 1)

    def test_index_engine_golden(self):
        with patch("rag_engine.indexing.index_engine.Embedder"), patch("rag_engine.indexing.index_engine.TextChunker"),patch("rag_engine.indexing.index_engine.VectorStore"),patch("rag_engine.indexing.index_engine.TXTLoader") as MockLoader,patch("rag_engine.indexing.index_engine.Document", MockDocument):
            
            from rag_engine.indexing.index_engine import IndexingEngine
            engine = IndexingEngine()
            
            MockLoader.return_value.load.return_value = [MockDocument("content")]
            engine.chunker.chunk_docs.return_value = [MockDocument("chunk")]
            
            with patch("os.path.exists", return_value=True), patch("os.path.isfile", return_value=True), patch("os.path.getsize", return_value=100),                  patch("os.access", return_value=True):
                 engine.index("test.txt")
                 engine.batch_index(["test.txt"])
