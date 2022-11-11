from scrapers.basescraper import BaseScraper, Cache, DEFAULT_DATA_DIR

import os
import json

TEST_DIR = os.path.join(DEFAULT_DATA_DIR, "test_data")
CACHE_FNAME = "test_cache.json"
CACHE_PATH = os.path.join(TEST_DIR, CACHE_FNAME)

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

def test_cache_init_no_cache_file():
    remove(CACHE_PATH)
    cache = Cache(TEST_DIR, CACHE_FNAME)
    assert os.path.exists(CACHE_PATH)
    assert load(CACHE_PATH) == {}
    assert cache.m_cache == {}

def test_cache_init_already_cache_file():
    test_data, cache = setup_cache_test_data()
    assert os.path.exists(cache.m_path)
    assert load(CACHE_PATH) == test_data
    assert cache.m_cache == test_data

def test_cache_get_item():
    test_data, cache = setup_cache_test_data()
    for k, v in test_data.items():
        assert cache[k] == v
    random_keys = ["aksdfasd", "asdjkfakld", "khkjaisen"]
    for k in random_keys:
        assert raises_exception(lambda : cache[k], KeyError)

def test_cache_set_item():
    remove(CACHE_PATH)
    cache = Cache(TEST_DIR, CACHE_FNAME)
    test_data = {
        'test': 'data', 
        'best': [2, 34, 5, 2]
        }
    for k, v in test_data.items():
        cache[k] = v
        assert cache[k] == v
        assert load(CACHE_PATH)[k] == v

def test_cache_get():
    test_data, cache = setup_cache_test_data()
    for k, v in test_data.items():
        assert cache.get(k) == v
        assert cache.get(1, list) == list
        assert cache.get(1, 10) == 10

def test_cache_is_cached():
    test_data, cache = setup_cache_test_data()
    for k, v in test_data.items():
        assert cache.is_cached(k)
        assert not cache.is_cached(k + "1")

def test_cache_update():
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

def main():
    test_cache_init_no_cache_file()
    test_cache_init_already_cache_file()
    test_cache_get_item()
    test_cache_set_item()
    test_cache_get()
    test_cache_is_cached()
    test_cache_update()

    print("All Tests for Cache and BaseScraper Classes Passed Successfully.")

if __name__ == "__main__":
    main()