import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from rag_engine.ingestion.loaders import PDFLoader
import os

class TestPDFLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #setup
        cls.sample_pdf = "sample.pdf"
        with open(cls.sample_pdf, "wb") as f:
            f.write(b"%PDF-1.4")

    def setUp(self):
        #before
        self.loader = PDFLoader()

    def tearDown(self):
        #after
        pass

    @classmethod
    def tearDownClass(cls):
        #cleanup
        if os.path.exists(cls.sample_pdf):
            os.remove(cls.sample_pdf)

    def test_import_error(self):
        #simulate missing pypdf
        import builtins
        original = builtins.__import__

        def fake_import(name, *a):
            if name == "pypdf":
                raise ImportError("need pypdf")
            return original(name, *a)

        builtins.__import__ = fake_import
        with self.assertRaises(ImportError):
            self.loader.load([self.sample_pdf])
        builtins.__import__ = original

    def test_ext_filter(self):
        #ignore non pdf
        out = self.loader.load(["a.txt"])
        self.assertEqual(len(out), 0)
        self.assertEqual(self.loader.count, 0)
        self.assertIsInstance(out, list)
        self.assertTrue(isinstance(self.loader.summary(), str))