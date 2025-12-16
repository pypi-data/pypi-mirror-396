import unittest
from rag_engine.ingestion.loaders import TXTLoader
import os

class TestTXTLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #setup
        cls.sample_txt = "t.txt"
        with open(cls.sample_txt, "w", encoding="utf-8") as f:
            f.write("hello")

    def setUp(self):
        #before
        self.loader = TXTLoader()

    def tearDown(self):
        #after
        pass

    @classmethod
    def tearDownClass(cls):
        #cleanup
        if os.path.exists(cls.sample_txt):
            os.remove(cls.sample_txt)

    def test_load_basic(self):
        #normal load
        out = self.loader.load([self.sample_txt])
        self.assertEqual(len(out), 1)
        self.assertEqual(self.loader.count, 1)
        self.assertEqual(out[0].page_content, "hello")
        self.assertEqual(out[0].metadata["type"], "txt")

    def test_ext_filter(self):
        #wrong ext
        out = self.loader.load(["bad.pdf"])
        self.assertEqual(len(out), 0)
        self.assertEqual(self.loader.count, 0)
        self.assertIsInstance(out, list)
        self.assertIn("txt", self.loader.summary())