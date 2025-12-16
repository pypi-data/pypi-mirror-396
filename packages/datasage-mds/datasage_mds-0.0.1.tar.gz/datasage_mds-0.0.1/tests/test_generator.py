import unittest
from unittest.mock import MagicMock, patch
import json
from rag_engine.retrieval.generator import LLMGenerator
from rag_engine.retrieval.data_models import Document

class TestGenerator(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.docs = [
            Document("Content 1", {"id": 1}),
            Document("Content 2", {"id": 2})
        ]
        cls.question = "What is this?"
        cls.mock_response_content = json.dumps({"response": "Mocked Answer"}).encode("utf-8")

    @classmethod
    def tearDownClass(cls):
        del cls.docs
        del cls.question
        del cls.mock_response_content

    def setUp(self):
        self.generator = LLMGenerator()
        # Create a mock response object structure
        self.mock_response = MagicMock()
        self.mock_response.status = 200
        self.mock_response.read.return_value = self.mock_response_content
        self.mock_response.__enter__.return_value = self.mock_response
        self.mock_response.__exit__.return_value = None

    def tearDown(self):
        del self.generator
        del self.mock_response

    @patch('rag_engine.retrieval.generator.urllib.request.urlopen')
    def test_generate_answer(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_response
        
        answer = self.generator.generate_answer(self.question, self.docs)
        
        self.assertEqual(answer, "Mocked Answer")
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer) > 0)
        self.assertTrue(mock_urlopen.called)

    @patch('rag_engine.retrieval.generator.urllib.request.urlopen')
    def test_summarize_docs(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_response
        
        summary = self.generator.summarize_docs(self.docs)
        
        self.assertEqual(summary, "Mocked Answer")
        self.assertIsInstance(summary, str)
        self.assertNotEqual(summary, "")
        self.assertTrue(mock_urlopen.called)
