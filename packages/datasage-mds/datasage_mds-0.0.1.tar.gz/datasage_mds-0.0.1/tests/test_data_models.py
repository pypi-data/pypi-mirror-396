import unittest
from rag_engine.retrieval.data_models import Document

class TestDataModels(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.sample_content = "This is a sample document content for testing purposes."
        cls.sample_metadata = {"source": "test_source", "author": "tester"}

    @classmethod
    def tearDownClass(cls):
        del cls.sample_content
        del cls.sample_metadata

    def setUp(self):
        self.doc_with_meta = Document(self.sample_content, self.sample_metadata)
        self.doc_no_meta = Document(self.sample_content)

    def tearDown(self):
        del self.doc_with_meta
        del self.doc_no_meta

    def test_document_initialization(self):
        # Assertions for doc_with_meta
        self.assertEqual(self.doc_with_meta.page_content, self.sample_content)
        self.assertEqual(self.doc_with_meta.metadata, self.sample_metadata)
        self.assertIsInstance(self.doc_with_meta.metadata, dict)
        self.assertIsInstance(self.doc_with_meta.page_content, str)
        
        # Assertions for doc_no_meta
        self.assertEqual(self.doc_no_meta.page_content, self.sample_content)
        self.assertEqual(self.doc_no_meta.metadata, {})

    def test_document_repr(self):
        repr_str = repr(self.doc_with_meta)
        
        self.assertIn("Document", repr_str)
        self.assertIn("page_content", repr_str)
        self.assertIn("metadata", repr_str)
        self.assertIsInstance(repr_str, str)
        
        # Check truncation in repr if content is long
        long_content = "a" * 100
        doc_long = Document(long_content)
        self.assertTrue(len(repr(doc_long)) < len(long_content) + 100) 
