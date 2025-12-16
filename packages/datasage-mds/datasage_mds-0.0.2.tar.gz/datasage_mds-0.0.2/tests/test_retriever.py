import unittest
from unittest.mock import MagicMock
from rag_engine.retrieval.retriever import Retriever, OllamaEmbedder
from rag_engine.retrieval.data_models import Document

class TestRetriever(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.query = "test query"
        cls.mock_embedding = [0.1, 0.2, 0.3]

    @classmethod
    def tearDownClass(cls):
        del cls.query
        del cls.mock_embedding

    def setUp(self):
        self.mock_vs = MagicMock()
        self.mock_embedder = MagicMock(spec=OllamaEmbedder)
        self.retriever = Retriever(self.mock_vs, self.mock_embedder)
        
        # Mock embedding return
        self.mock_embedder.embed_query.return_value = self.mock_embedding

    def tearDown(self):
        del self.retriever
        del self.mock_vs
        del self.mock_embedder

    def test_retrieve(self):
        # Mock vector store return
        mock_doc_result = MagicMock()
        mock_doc_result.page_content = "Result Content"
        mock_doc_result.metadata = {"id": 1}
        self.mock_vs.store.similarity_search_by_vector.return_value = [mock_doc_result]
        
        results = self.retriever.retrieve(self.query)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], Document)
        self.assertEqual(results[0].page_content, "Result Content")
        self.mock_embedder.embed_query.assert_called_with(self.query)

    def test_retrieve_with_scores(self):
        # Mock vector store return for scores
        mock_doc_result = MagicMock()
        mock_doc_result.page_content = "Result Content"
        mock_doc_result.metadata = {"id": 1}
        self.mock_vs.store.similarity_search_with_score.return_value = [(mock_doc_result, 0.95)]
        
        results = self.retriever.retrieve_with_scores(self.query)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], tuple)
        self.assertIsInstance(results[0][0], Document)
        self.assertEqual(results[0][1], 0.95)
        self.mock_vs.store.similarity_search_with_score.assert_called_with(self.query, k=5)
