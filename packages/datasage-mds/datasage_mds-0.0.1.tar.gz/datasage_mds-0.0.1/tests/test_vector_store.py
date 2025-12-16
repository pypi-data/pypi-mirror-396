import shutil
import time
import gc
import os

def robust_teardown(cls):
    # Helper to forcefully clean up ChromaDB on Windows
    if hasattr(cls, 'indexer'): del cls.indexer
    if hasattr(cls, 'vector_store'): del cls.vector_store
    gc.collect()
    time.sleep(0.5)
    if hasattr(cls, 'test_dir') and os.path.exists(cls.test_dir):
        for i in range(3):
            try:
                shutil.rmtree(cls.test_dir)
                break
            except PermissionError:
                time.sleep(1.0)
"""
Unit tests for the VectorStore module.
Tests document storage, retrieval, and analytics with error handling.
"""

import unittest
import sys
import os
import shutil
from langchain_core.documents import Document

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)

from rag_engine.indexing.embedder import Embedder
from rag_engine.indexing.vector_store import VectorStore


class TestVectorStoreInitialization(unittest.TestCase):
    """Test cases for VectorStore initialization."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestVectorStoreInitialization ===")
        cls.embedder = Embedder()
        cls.test_dir = "./test_vs_init"
    
    @classmethod
    def tearDownClass_OLD(cls):
        """Clean up class-level resources."""
        print("=== Finished TestVectorStoreInitialization ===")
        del cls.embedder
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up test fixtures."""
        self.vector_store = None
    
    def tearDown(self):
        """Clean up after each test."""
        if self.vector_store:
            del self.vector_store
    
    def test_initialization_with_persist_dir(self):
        """Test vector store initialization with persistence."""
        self.vector_store = VectorStore(
            embedding_model=self.embedder.model,
            persist_dir=self.test_dir
        )
        
        self.assertIsNotNone(self.vector_store, "VectorStore should be created")
        self.assertEqual(self.vector_store.persist_dir, self.test_dir,
                        "Persist directory should match")
        self.assertEqual(self.vector_store._doc_count, 0,
                        "Document count should start at 0")
        self.assertIsInstance(self.vector_store._metadata_index, dict,
                             "Metadata index should be dictionary")
    
    def test_initialization_without_persist_dir(self):
        """Test vector store initialization without persistence."""
        self.vector_store = VectorStore(
            embedding_model=self.embedder.model,
            persist_dir=None
        )
        self.assertIsNotNone(self.vector_store, "VectorStore should be created")
        self.assertIsNone(self.vector_store.persist_dir,
                         "Persist directory should be None")
        self.assertIsNotNone(self.vector_store.store,
                            "Store should be initialized")
        self.assertEqual(self.vector_store._doc_count, 0,
                        "Document count should start at 0")


class TestVectorStoreAddDocuments(unittest.TestCase):
    """Test cases for adding documents to vector store."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestVectorStoreAddDocuments ===")
        cls.embedder = Embedder()
        cls.test_dir = "./test_vs_add"
    
    @classmethod
    def tearDownClass_OLD(cls):
        """Clean up class-level resources."""
        print("=== Finished TestVectorStoreAddDocuments ===")
        del cls.embedder
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up test fixtures."""
        self.vector_store = VectorStore(
            embedding_model=self.embedder.model,
            persist_dir=self.test_dir
        )
        self.test_docs = [
            Document(
                page_content="Python is a programming language",
                metadata={"path": "test1.txt", "type": "txt"}
            ),
            Document(
                page_content="Machine learning uses data",
                metadata={"path": "test2.txt", "type": "txt"}
            )
        ]
    
    def tearDown(self):
        """Clean up after each test."""
        del self.vector_store
    
    def test_add_single_document(self):
        """Test adding a single document."""
        docs = [self.test_docs[0]]
        doc_ids = self.vector_store.add_documents(docs)
        
        self.assertIsNotNone(doc_ids, "Document IDs should not be None")
        self.assertEqual(len(doc_ids), 1, "Should return 1 ID")
        self.assertEqual(doc_ids[0], "doc_000000", "First ID should be doc_000000")
        self.assertEqual(self.vector_store._doc_count, 1,
                        "Document count should be 1")
    
    def test_add_multiple_documents(self):
        """Test adding multiple documents."""
        docs = self.test_docs
        doc_ids = self.vector_store.add_documents(docs)
        self.assertEqual(len(doc_ids), len(docs), "Should return ID for each doc")
        self.assertEqual(self.vector_store._doc_count, len(docs),
                        "Document count should match")
        self.assertTrue(all(id.startswith("doc_") for id in doc_ids),
                       "All IDs should start with 'doc_'")
        self.assertEqual(len(set(doc_ids)), len(doc_ids),
                        "All IDs should be unique")
    
    def test_add_documents_metadata_tracking(self):
        """Test metadata is properly tracked."""
        docs = [self.test_docs[0]]
        
        doc_ids = self.vector_store.add_documents(docs)
        doc_id = doc_ids[0]
        
        self.assertIn(doc_id, self.vector_store._metadata_index,
                     "Doc ID should be in metadata index")
        metadata = self.vector_store._metadata_index[doc_id]
        self.assertIn("source", metadata, "Should have source")
        self.assertIn("timestamp", metadata, "Should have timestamp")
        self.assertIn("content_length", metadata, "Should have content_length")
    
    def test_add_empty_document_list(self):
       """Test adding empty document list (error handling)."""
       docs = []
       with self.assertRaises(ValueError) as context:
           self.vector_store.add_documents(docs)
       self.assertIn("non-empty", str(context.exception))


class TestVectorStoreSearch(unittest.TestCase):
    """Test cases for searching documents."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestVectorStoreSearch ===")
        cls.embedder = Embedder()
        cls.test_dir = "./test_vs_search"
        cls.vector_store = VectorStore(
            embedding_model=cls.embedder.model,
            persist_dir=cls.test_dir
        )
        
        test_docs = [
            Document(
                page_content="Python programming language",
                metadata={"path": "python.txt", "type": "txt"}
            ),
            Document(
                page_content="Machine learning algorithms",
                metadata={"path": "ml.txt", "type": "txt"}
            ),
            Document(
                page_content="Deep learning neural networks",
                metadata={"path": "dl.txt", "type": "txt"}
            )
        ]
        cls.vector_store.add_documents(test_docs)
    
    @classmethod
    def tearDownClass_OLD(cls):
        """Clean up class-level resources."""
        print("=== Finished TestVectorStoreSearch ===")
        del cls.vector_store
        del cls.embedder
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_search_basic(self):
        """Test basic search functionality."""
        query = "programming"
        results = self.vector_store.search(query, k=2)
        
        self.assertIsNotNone(results, "Results should not be None")
        self.assertLessEqual(len(results), 2, "Should return at most k results")
        self.assertTrue(all(isinstance(doc, Document) for doc in results),
                       "All results should be Documents")
        self.assertTrue(all("search_rank" in doc.metadata for doc in results),
                       "All results should have search_rank")
    
    def test_search_with_k_parameter(self):
        """Test search with different k values."""
        query = "learning"
        k = 1
        
        results = self.vector_store.search(query, k=k)
        self.assertLessEqual(len(results), k, f"Should return at most {k} results")
        self.assertGreater(len(results), 0, "Should return at least 1 result")
        self.assertEqual(results[0].metadata['search_rank'], 1,
                        "First result should have rank 1")
        self.assertAlmostEqual(results[0].metadata['relevance_score'], 1.0,
                              "First result should have score 1.0")
    
    def test_search_empty_query(self):
        """Test search with empty query (error handling)."""
        query = ""
        try:
            results = self.vector_store.search(query, k=2)
            self.assertIsNotNone(results, "Should handle empty query")
            self.assertIsInstance(results, list, "Should return list")
        except Exception as e:
            self.assertIsInstance(e, Exception, "Should raise an exception")
    
    def test_search_statistics_tracking(self):
        """Test that searches are tracked in statistics."""
        initial_count = self.vector_store._search_stats['total_searches']
        query = "algorithms"
        
        self.vector_store.search(query, k=2)
        
        final_count = self.vector_store._search_stats['total_searches']
        self.assertEqual(final_count, initial_count + 1,
                        "Search count should increment")
        self.assertIn(query, self.vector_store._search_stats['unique_queries'],
                     "Query should be recorded")
        self.assertGreater(self.vector_store._search_stats['total_results_returned'], 0,
                          "Should have returned results")


class TestVectorStoreUtilities(unittest.TestCase):
    """Test cases for utility methods."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestVectorStoreUtilities ===")
        cls.embedder = Embedder()
        cls.test_dir = "./test_vs_utils"
        cls.vector_store = VectorStore(
            embedding_model=cls.embedder.model,
            persist_dir=cls.test_dir
        )
        
        test_docs = [
            Document(
                page_content="Document 1",
                metadata={"path": "file1.txt", "type": "txt"}
            ),
            Document(
                page_content="Document 2",
                metadata={"path": "file2.txt", "type": "txt"}
            ),
            Document(
                page_content="Document 3",
                metadata={"path": "file1.txt", "type": "txt"}
            )
        ]
        cls.vector_store.add_documents(test_docs)
    
    @classmethod
    def tearDownClass_OLD(cls):
        """Clean up class-level resources."""
        print("=== Finished TestVectorStoreUtilities ===")
        del cls.vector_store
        del cls.embedder
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_get_sources(self):
        """Test getting list of sources."""
        sources = self.vector_store.get_sources()
        self.assertIsNotNone(sources, "Sources should not be None")
        self.assertIsInstance(sources, list, "Sources should be a list")
        self.assertGreater(len(sources), 0, "Should have at least one source")
        self.assertIn("file1.txt", sources, "Should contain file1.txt")
    
    def test_get_document_count_by_source(self):
        """Test getting document count by source."""
        source = "file1.txt"        
        count = self.vector_store.get_document_count_by_source(source)     
        self.assertIsInstance(count, int, "Count should be integer")
        self.assertEqual(count, 2, "file1.txt should have 2 documents")
        self.assertGreaterEqual(count, 0, "Count should be non-negative")
        self.assertLessEqual(count, 3, "Count should not exceed total docs")
    
    def test_get_statistics(self):
        """Test getting comprehensive statistics."""
        stats = self.vector_store.get_statistics()       
        self.assertIsNotNone(stats, "Statistics should not be None")
        self.assertIsInstance(stats, dict, "Statistics should be dictionary")
        self.assertIn("total_documents", stats, "Should have total_documents")
        self.assertIn("unique_sources", stats, "Should have unique_sources")
        self.assertEqual(stats['total_documents'], 3, "Should have 3 documents")
    
    def test_get_document_info(self):
        """Test getting information for specific document."""
        doc_id = "doc_000000"
        info = self.vector_store.get_document_info(doc_id)
        self.assertIsNotNone(info, "Info should not be None")
        self.assertIsInstance(info, dict, "Info should be dictionary")
        self.assertIn("source", info, "Should have source")
        self.assertIn("timestamp", info, "Should have timestamp")


if __name__ == '__main__':
    unittest.main(verbosity=2)