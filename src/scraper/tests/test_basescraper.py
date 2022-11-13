from scrapers.basescraper import BaseScraper, Cache
from .test_settings import TEST_DIR, CACHE_FNAME, CACHE_PATH

import os
import json
import unittest

def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

def load(path):
    with open(path, "r") as f:
        return json.load(f)

def remove(path):
    if os.path.exists(path):
        os.remove(path)

def raises_exception(func, exception):
    try:
        func()
    except exception:
        return True
    return False

def setup_cache_test_data():
    test_data = {"test" : "data", "list" : [1, 1, 1, 2, 3],  
                "nested" : 
                    {
                        "1nested" : "1nested value",
                        "2nested" : "2nested value",
                    }
                }
    save(CACHE_PATH, test_data)
    cache = Cache(TEST_DIR, CACHE_FNAME)
    return test_data, cache


class TestCache(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.test_dir = TEST_DIR

    def test_cache_init_no_cache_file(self):
        remove(CACHE_PATH)
        cache = Cache(self.test_dir, CACHE_FNAME)
        assert os.path.exists(CACHE_PATH)
        assert load(CACHE_PATH) == {}
        assert cache.m_cache == {}

    def test_cache_init_already_cache_file(self):
        test_data, cache = setup_cache_test_data()
        assert os.path.exists(cache.m_path)
        assert load(CACHE_PATH) == test_data
        assert cache.m_cache == test_data

    def test_cache_get_item(self):
        test_data, cache = setup_cache_test_data()
        for k, v in test_data.items():
            assert cache[k] == v
        random_keys = ["aksdfasd", "asdjkfakld", "khkjaisen"]
        for k in random_keys:
            with self.assertRaises(KeyError):
                cache[k]

    def test_cache_set_item(self):
        remove(CACHE_PATH)
        cache = Cache(self.test_dir, CACHE_FNAME)
        test_data = {
            'test': 'data', 
            'best': [2, 34, 5, 2]
            }
        for k, v in test_data.items():
            cache[k] = v
            assert cache[k] == v
            assert load(CACHE_PATH)[k] == v

    def test_cache_get(self):
        test_data, cache = setup_cache_test_data()
        for k, v in test_data.items():
            assert cache.get(k) == v
            assert cache.get(1, list) == list
            assert cache.get(1, 10) == 10

    def test_cache_is_cached(self):
        test_data, cache = setup_cache_test_data()
        for k, v in test_data.items():
            assert cache.is_cached(k)
            assert not cache.is_cached(k + "1")

    def test_cache_update(self):
        test_data, cache = setup_cache_test_data()
        cache.update("nested", {
                    "1nested" : "10nested value"
                })

        assert cache["nested"] == {
                    "1nested" : "10nested value",
                    "2nested" : "2nested value",
                }, cache["nested"]
        cache.update("nested", {
                    "2nested" : "10nested value"
                })
        assert cache["nested"] == {
                    "1nested" : "10nested value",
                    "2nested" : "10nested value",
                }

class TestBaseScraper(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.url = "https://test/test"
        self.output_dir = TEST_DIR
        self.scraper = BaseScraper(self.url, self.output_dir)

    def test_init(self):
        self.assertEqual(self.url, self.scraper.m_base_url)
        self.assertEqual(self.output_dir, self.scraper.m_output_dir)

    def test_save_file(self):
        test_data = {"12341234" : "askdjfalksdf", "98742" : "asdfasdkj"}
        output_file = os.path.join(self.output_dir, "testtest.json")
        self.scraper._save_file(output_file, test_data)

        self.assertEqual(True, os.path.exists(output_file))
        data = load(output_file)
        self.assertEqual(data, test_data)

    def test_load_file(self):
        test_data = {"12341234" : "askdjfalksdf", "98742" : "asdfasdkj"}
        output_file = os.path.join(self.output_dir, "testtest.json")
        uncreated_file = os.path.join(self.output_dir, "unknown.json")
        save(output_file, test_data)

        data = self.scraper._load_file(output_file)
        self.assertEqual(data, test_data)

        with self.assertRaises(AssertionError):
            self.scraper._load_file(uncreated_file)