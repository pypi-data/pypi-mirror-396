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
Unit tests for the IndexingEngine module.
Tests file indexing, validation, and orchestration with error handling.
"""

import unittest
import sys
import os
import shutil
import time
import gc



current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)


from rag_engine.indexing.index_engine import (
    IndexingEngine,
    IndexingException,
    FileValidationError,
    LoaderError,
    ChunkingError,
    StorageError
)


class TestIndexingEngineInitialization(unittest.TestCase):
    """Test cases for IndexingEngine initialization."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestIndexingEngineInitialization ===")
        cls.test_dir = "./test_ie_init"
    
    @classmethod
    def tearDownClass(cls):
        robust_teardown(cls)