import os
import pathlib

TEST_DIR = os.path.join(str(pathlib.Path(os.path.dirname(__file__)).parent), "data/test_data")
CACHE_FNAME = "test_cache.json"
CACHE_PATH = os.path.join(TEST_DIR, CACHE_FNAME)