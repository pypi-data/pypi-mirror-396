"""
Unit tests for the Embedder module.
Tests embedding functionality with error handling and edge cases.
"""

import unittest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)

from rag_engine.indexing.embedder import Embedder


class TestEmbedderInitialization(unittest.TestCase):
    """Test cases for Embedder initialization and configuration."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources (runs once before all tests)."""
        print("\n=== Starting TestEmbedderInitialization ===")
        cls.default_model = "all-MiniLM-L6-v2"
        cls.test_model = "all-MiniLM-L6-v2"
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources (runs once after all tests)."""
        print("=== Finished TestEmbedderInitialization ===")
    
    def setUp(self):
        """Set up test fixtures (runs before each test)."""
        self.embedder = None
    
    def tearDown(self):
        """Clean up after each test (runs after each test)."""
        if self.embedder:
            del self.embedder
    
    def test_default_initialization(self):
        """Test embedder initialization with default parameters."""
        self.embedder = Embedder()
        self.assertIsNotNone(self.embedder, "Embedder should be created")
        self.assertIsNotNone(self.embedder.model, "Model should be initialized")
        self.assertEqual(self.embedder.model_name, self.default_model, 
                        "Model name should be default")
        self.assertTrue(hasattr(self.embedder, '_preprocess_text'),
                       "Should have preprocessing method")
    
    def test_custom_model_initialization(self):
        """Test embedder initialization with custom model."""
        self.embedder = Embedder(model_name=self.test_model)
        self.assertIsNotNone(self.embedder, "Embedder should be created")
        self.assertEqual(self.embedder.model_name, self.test_model,
                        "Model name should match custom model")
        self.assertIsNotNone(self.embedder.model, "Model should be initialized")
        self.assertTrue(callable(self.embedder.embed_query),
                       "embed_query should be callable")


class TestEmbedderTextPreprocessing(unittest.TestCase):
    """Test cases for text preprocessing functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestEmbedderTextPreprocessing ===")
        cls.embedder = Embedder()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestEmbedderTextPreprocessing ===")
        del cls.embedder
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_texts = {
            'normal': "Hello world",
            'whitespace': "  Hello   world  ",
            'newlines': "Hello\nworld\n",
            'tabs': "Hello\tworld"
        }
    
    def tearDown(self):
        """Clean up after each test."""
        self.test_texts.clear()
    
    def test_preprocess_normal_text(self):
        """Test preprocessing of normal text."""
        text = self.test_texts['normal']
        result = self.embedder._preprocess_text(text)
        self.assertEqual(result, "Hello world", "Normal text should be unchanged")
        self.assertIsInstance(result, str, "Result should be string")
        self.assertNotIn("  ", result, "Should not have double spaces")
        self.assertEqual(result.strip(), result, "Should not have leading/trailing spaces")
    
    def test_preprocess_whitespace(self):
        """Test preprocessing removes extra whitespace."""
        text = self.test_texts['whitespace']
        result = self.embedder._preprocess_text(text)
    
        self.assertEqual(result, "Hello world", "Extra whitespace should be removed")
        self.assertNotEqual(result, text, "Result should differ from input")
        self.assertNotIn("  ", result, "Should not have double spaces")
        self.assertEqual(len(result.split()), 2, "Should have exactly 2 words")


class TestEmbedderQueryEmbedding(unittest.TestCase):
    """Test cases for single query embedding."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestEmbedderQueryEmbedding ===")
        cls.embedder = Embedder()
        cls.expected_dimension = 384
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestEmbedderQueryEmbedding ===")
        del cls.embedder
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_queries = [
            "machine learning",
            "artificial intelligence",
            "deep learning networks"
        ]
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_embed_single_query(self):
        """Test embedding a single query."""
        query = self.sample_queries[0]
        
        embedding = self.embedder.embed_query(query)
        self.assertIsNotNone(embedding, "Embedding should not be None")
        self.assertIsInstance(embedding, list, "Embedding should be a list")
        self.assertEqual(len(embedding), self.expected_dimension,
                        f"Embedding should have {self.expected_dimension} dimensions")
        self.assertTrue(all(isinstance(x, float) for x in embedding),
                       "All elements should be floats")
    
    def test_embed_empty_string(self):
        """Test embedding an empty string (error handling)."""
        query = ""
        try:
            embedding = self.embedder.embed_query(query)
            self.assertIsNotNone(embedding, "Should handle empty string")
            self.assertEqual(len(embedding), self.expected_dimension,
                           "Should still return proper dimension")
        except Exception as e:
            self.fail(f"Should not raise exception for empty string: {e}")
    
    def test_embed_special_characters(self):
        """Test embedding text with special characters."""
        query = "Hello! @#$ %^& *()"

        embedding = self.embedder.embed_query(query)
        
        self.assertIsNotNone(embedding, "Should handle special characters")
        self.assertEqual(len(embedding), self.expected_dimension,
                        "Should return proper dimension")
        self.assertTrue(all(isinstance(x, float) for x in embedding),
                       "All elements should be floats")
        self.assertFalse(any(x != x for x in embedding), # Check for NaN
                        "Should not contain NaN values")
    
    def test_embed_long_text(self):
        """Test embedding very long text."""
        # Arrange
        query = "machine learning " * 100  # 1600 characters
        
        # Act
        embedding = self.embedder.embed_query(query)
        
        # Assert
        self.assertIsNotNone(embedding, "Should handle long text")
        self.assertEqual(len(embedding), self.expected_dimension,
                        "Should return proper dimension")
        self.assertIsInstance(embedding, list, "Should return list")
        self.assertTrue(len(embedding) > 0, "Should not be empty")


class TestEmbedderBatchProcessing(unittest.TestCase):
    """Test cases for batch document embedding."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestEmbedderBatchProcessing ===")
        cls.embedder = Embedder()
        cls.expected_dimension = 384
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestEmbedderBatchProcessing ===")
        del cls.embedder
    
    def setUp(self):
        """Set up test fixtures."""
        self.batch_texts = [
            "Document 1",
            "Document 2",
            "Document 3",
            "Document 4",
            "Document 5"
        ]
    
    def tearDown(self):
        """Clean up after each test."""
        self.batch_texts.clear()
    
    def test_embed_multiple_documents(self):
        """Test embedding multiple documents."""
        # Arrange
        texts = self.batch_texts
        
        # Act
        embeddings = self.embedder.embed_documents(texts, show_progress=False)
        
        # Assert
        self.assertIsNotNone(embeddings, "Embeddings should not be None")
        self.assertEqual(len(embeddings), len(texts),
                        "Should have same number of embeddings as texts")
        self.assertTrue(all(len(emb) == self.expected_dimension for emb in embeddings),
                       f"All embeddings should have {self.expected_dimension} dimensions")
        self.assertTrue(all(isinstance(emb, list) for emb in embeddings),
                       "All embeddings should be lists")
    
    def test_embed_empty_list(self):
        """Test embedding an empty list (error handling)."""
        texts = []
        embeddings = self.embedder.embed_documents(texts)
        self.assertIsNotNone(embeddings, "Should handle empty list")
        self.assertEqual(len(embeddings), 0, "Should return empty list")
        self.assertIsInstance(embeddings, list, "Should return list")
        self.assertEqual(embeddings, [], "Should be empty list")
    
    def test_embed_single_document_batch(self):
        """Test batch embedding with single document."""
        texts = ["Single document"]
        embeddings = self.embedder.embed_documents(texts)
        self.assertEqual(len(embeddings), 1, "Should return single embedding")
        self.assertEqual(len(embeddings[0]), self.expected_dimension,
                        "Should have correct dimension")
        self.assertIsInstance(embeddings[0], list, "Should be list")
        self.assertTrue(all(isinstance(x, float) for x in embeddings[0]),
                       "All elements should be floats")
    
    def test_embed_with_progress_tracking(self):
        """Test batch embedding with progress tracking."""
        texts = ["Doc " + str(i) for i in range(15)]  # 15 docs to trigger progress
        embeddings = self.embedder.embed_documents(texts, show_progress=True)
        self.assertEqual(len(embeddings), len(texts),
                        "Should process all documents")
        self.assertTrue(all(len(emb) == self.expected_dimension for emb in embeddings),
                       "All embeddings should have correct dimension")
        self.assertIsNotNone(embeddings, "Should complete successfully")
        self.assertIsInstance(embeddings, list, "Should return list")


class TestEmbedderUtilityMethods(unittest.TestCase):
    """Test cases for utility methods."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestEmbedderUtilityMethods ===")
        cls.embedder = Embedder()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestEmbedderUtilityMethods ===")
        del cls.embedder
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_get_embedding_dimension(self):
        """Test getting embedding dimension."""
        dimension = self.embedder.get_embedding_dimension()
        self.assertIsNotNone(dimension, "Dimension should not be None")
        self.assertIsInstance(dimension, int, "Dimension should be integer")
        self.assertEqual(dimension, 384, "Should be 384 for all-MiniLM-L6-v2")
        self.assertGreater(dimension, 0, "Dimension should be positive")
    
    def test_model_name_attribute(self):
        """Test model_name attribute is accessible."""
        model_name = self.embedder.model_name
        self.assertIsNotNone(model_name, "Model name should not be None")
        self.assertIsInstance(model_name, str, "Model name should be string")
        self.assertEqual(model_name, "all-MiniLM-L6-v2", "Should match default")
        self.assertGreater(len(model_name), 0, "Should not be empty")


if __name__ == '__main__':
    unittest.main(verbosity=2)