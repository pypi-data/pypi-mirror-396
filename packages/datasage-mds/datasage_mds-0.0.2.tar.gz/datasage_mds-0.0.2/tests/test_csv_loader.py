import unittest
from rag_engine.ingestion.loaders import CSVLoader
import csv
import os

class TestCSVLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #setup
        cls.sample_csv = "t.csv"
        with open(cls.sample_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["name","age"])
            w.writerow(["A","1"])
            w.writerow(["B","2"])

    def setUp(self):
        #before
        self.loader = CSVLoader()

    def tearDown(self):
        #after
        pass

    @classmethod
    def tearDownClass(cls):
        #cleanup
        if os.path.exists(cls.sample_csv):
            os.remove(cls.sample_csv)

    def test_load_rows(self):
        #load rows
        out = self.loader.load([self.sample_csv])
        self.assertEqual(len(out), 2)
        self.assertEqual(self.loader.count, 2)
        self.assertIn("row", out[0].metadata)
        self.assertEqual(out[0].metadata["type"], "csv")

    def test_wrong_ext(self):
        #ignore non csv
        out = self.loader.load(["x.txt"])
        self.assertEqual(len(out), 0)
        self.assertEqual(self.loader.count, 0)
        self.assertIsInstance(out, list)
        self.assertIn("csv", self.loader.summary())