import unittest
from rag_engine.ingestion.chunker import TextChunker
from langchain_core.documents import Document

class TestTextChunker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #setup
        cls.long_text = "a"*2500

    def setUp(self):
        #before
        self.ch = TextChunker(chunk_size=1000, overlap=200)

    def tearDown(self):
        #after
        pass

    @classmethod
    def tearDownClass(cls):
        #end
        pass

    def test_chunking(self):
        #split doc
        doc = Document(page_content=self.long_text, metadata={"x":1})
        out = self.ch.chunk_one(doc)
        self.assertTrue(len(out) > 1)
        self.assertIsInstance(out, list)
        self.assertIsInstance(out[0].page_content, str)
        self.assertEqual(out[0].metadata["x"], 1)

    def test_set_size(self):
        #change size
        self.ch.set_size(500)
        self.assertEqual(self.ch.chunk_size, 500)
        doc = Document(page_content="a"*1500)
        out = self.ch.chunk_one(doc)
        self.assertTrue(len(out) >= 3)
        self.assertIsInstance(out, list)
        self.assertTrue(all(isinstance(d.page_content, str) for d in out))