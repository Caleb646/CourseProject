import os
import json
import pathlib

import requests
from requests import cookies

DEFAULT_DATA_DIR = os.path.join(str(pathlib.Path(os.path.dirname(__file__)).parent), "data/")

class Cache:
    def __init__(self, _dir, fname):
        self.m_dir = _dir
        self.m_fname = fname
        self.m_path = os.path.join(_dir, fname)
        self.m_cache = {}
        self.m_loaded = False
        if not os.path.exists(self.m_path):
            os.makedirs(self.m_dir, exist_ok=True) # create dir
            self._write_to_cache_file({}) # create empty cache file
        self.m_cache = self._load_cache_file()

    def __getitem__(self, key):
        return self.read(key)

    def __setitem__(self, key, value):
        self.write(key, value)

    def get(self, key, default_value=None):
        return self.m_cache.get(key, default_value)

    def is_cached(self, key):
        return self.m_cache.get(key, False)

    def update(self, key, value):
        if key in self.m_cache:
            assert isinstance(self.m_cache[key], dict), \
                "Update can only be used when the value returned by key [{}] is of type dict".format(key)
            self.m_cache[key].update(value)
        else:
            self.m_cache[key] = value
        self._write_to_cache_file(self.m_cache)

    def read(self, key):
        return self.m_cache[key]

    def write(self, key, data):
        self.m_cache[key] = data
        self._write_to_cache_file(self.m_cache)

    def clear(self, key=None):
        if not key: # clear whole file
            self._write_to_cache_file({})
            return
        if key not in self.m_cache:
            return
        self.m_cache.pop(key) # remove only part of the cache
        self._write_to_cache_file(self.m_cache)

    def _write_to_cache_file(self, data):
        data = json.dumps(data)
        with open(self.m_path, "w") as f:
            f.writelines(data)

    def _load_cache_file(self):
        with open(self.m_path, "r") as f:
            self.m_loaded = True
            return json.load(f)  


class BaseScraper:
    def __init__(self, base_url, output_dir = DEFAULT_DATA_DIR):
        self.m_base_url = base_url
        self.m_output_dir = output_dir
        self.m_cookie_jar = cookies.RequestsCookieJar()

    def _requests_get(self, url, with_cookies = True):
        print("Making get request to [{}] with cookies [{}]".format(url, with_cookies))
        if with_cookies:
            return requests.get(url, cookies=self.m_cookie_jar)
        return requests.get(url)

    def _clean_selenium_cookie(self, cookie, valid_fields=("name", "value", "domain", "sameSite")):
        res = {}
        for f in valid_fields:
            if f in cookie:
                res[f] = cookie[f]
        return res

    def _clean_requests_cookie(self, cookie, valid_fields=("name", "value", "path", "domain", "port", "secure", "expires")):
        res = {}
        if "expiry" in cookie:
            res["expires"] = cookie["expiry"]
        if "httpOnly" in cookie:
            res["rest"] = {'HttpOnly': cookie['httpOnly']}
        for f in valid_fields:
            if f in cookie:
                res[f] = cookie[f]
        return res

    def _set_cookies(self, ccookies):
        assert isinstance(ccookies, list)
        for c in ccookies:
            c = self._clean_requests_cookie(c)
            cookie = cookies.create_cookie(**c)
            self.m_cookie_jar.set_cookie(cookie)

    def _save_file(self, output_path, data):
        _dir, _ = os.path.split(output_path)
        os.makedirs(_dir, exist_ok=True)
        data = json.dumps(data)
        with open(output_path, mode="w") as f:
            f.writelines(data)

    def _load_file(self, path):
        assert os.path.exists(path), "Path [{}] does not exist".format(path)
        with open(path, mode="r") as f:
            return json.load(f)

if __name__ == "__main__":
    BaseScraper("")