from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

import os
import time
import re
from functools import partial

from .basescraper import BaseScraper, Cache, DEFAULT_DATA_DIR

# TODO Urls need to be removed if they contain the words "exam", "quiz" or they don't contain 
# the class id "cs-410"

# TODO Returned cookies from successful login with email and password in headless=True are not valid. Cookies have to be gotten
# with headless=False first then cached. 

def rule_factory(func, *args, **kwargs):
    return partial(func, *args, **kwargs)

def fvalid(keyword, url: str, valid=lambda keyword, url : keyword in url):
    """
    param: valid -> is a lambda function that returns true if the url is valid
    """
    url = url.lower()
    if isinstance(keyword, str):
        return valid(keyword, url)
    if isinstance(keyword, set):
        return valid(keyword, url)
    is_valid = True
    for key in keyword:
        is_valid &= valid(key, url)
    return is_valid

# return true if the url is valid
def rvalid(pattern, url: str):
    url = url.lower()
    return re.search(pattern, url) is None    

class CouseraScraper(BaseScraper):
    
    def __init__(self, base_url, email, password, url_rules=(), *args, **kwargs):
        kwargs.setdefault("output_dir", os.path.join(DEFAULT_DATA_DIR, "coursera/"))
        BaseScraper.__init__(self, base_url, *args, **kwargs)

        self.m_email = email
        self.m_password = password

        # cache keys
        self.m_cookies_cache_key = "cookies"
        self.m_seen_urls_cache_key = "seen_urls"
        self.m_to_process_urls_cache_key = "to_process_urls"
        self.m_page_content_cache_key = "content"
        self.m_page_text_cache_key = "text"

        self.m_output_fname = "coursera_content.json"
        self.m_output_path = os.path.join(self.m_output_dir, self.m_output_fname)

        # remove grades from text content
        self.m_page_content_regex = re.compile("([0-9]{1,3}%)|(%[0-9]{1,3})")

        # controls the cache file that stores the cookies, seen and to be processed urls and content for all pages.
        self.m_cache = Cache(self.m_output_dir, "cache.json")
        
        # sets cannot be serialized only lists so they need to be converted to sets
        self.m_seen_urls = set(self.m_cache.get(self.m_seen_urls_cache_key, set()))
        self.m_to_process_urls = set(self.m_cache.get(self.m_to_process_urls_cache_key, set()))

        # these rules control what urls are considered valid or not
        self.m_url_rules = [
                rule_factory(fvalid, keyword=["cs-410", "www.coursera.org"]),
                rule_factory(fvalid, keyword=self.m_seen_urls, valid=lambda keyword, url : url not in keyword),
                rule_factory(fvalid, keyword=[
                        "quiz", "exam", "grades", "notes", "course-inbox", "assignments", "#"
                    ], valid=lambda keyword, url : keyword not in url), 
                rule_factory(rvalid, pattern="mp[0-9]"),
            ]
        # can add additional rules
        if url_rules:
            self.m_url_rules.extend(url_rules)

    def init_driver(self, chrome_driver_path, headless=True):
        assert os.path.exists(chrome_driver_path), "Chrome driver path doesn't exist [{}]".format(chrome_driver_path)
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
        self.m_driver = webdriver.Chrome(chrome_driver_path, options=chrome_options)
        print("Successfully started Chrome driver.")

    def _wait_until(self, name, timeout=10, by=By.ID) -> WebElement:
        try:
            element = WebDriverWait(self.m_driver, timeout=timeout).until(
                EC.presence_of_element_located((by, name))
            )
            return element, None
        except TimeoutException as e: # Failed to find the element given the timeout
            print("[ERROR] Failed to locate element by [{}] with name [{}] because [{}]".format(by, name, str(e)))
            return None, e      

    def _setup_cookies(self, test_url=None):
        cookies = self.m_cache[self.m_cookies_cache_key]
        self._set_cookies(cookies)
        valid = self._test_auth(test_url)
        if not valid:
            print("Cookies were not valid. Removing them from the cache.")
            self.m_cache.clear(self.m_cookies_cache_key)
        return valid
        
    def _set_cookies(self, ccookies):
        super()._set_cookies(ccookies) # set cookies in requests cookie jar
        for c in ccookies:
            c = self._clean_selenium_cookie(c)
            self.m_driver.add_cookie(c)

    def _test_auth(self, test_url=None):
        if not test_url:
            test_url = "{}/{}".format(self.m_base_url, "learn/cs-410/home/week/1")
        print("Testing cookies with url [{}]".format(test_url))

        _, error = self._wait_until("rc-ModuleLessons", by=By.CLASS_NAME)
        if error:
            print("Cookies invalid for [{}] because [{}]".format(test_url, str(error)))
            # remove invalid cookies
            self.m_cache.clear(self.m_cookies_cache_key)
            return False
        return True

    def _url_weeks(self, cclass="cs-410", start=1, stop=17):
        for i in range(start, stop):
            yield "{}/learn/{}/home/week/{}".format(self.m_base_url, cclass, i)
    
    def _login(self, email, password):
        url = "{}/?authMode=login".format(self.m_base_url)
        self.m_driver.get(url)
        # NOTE When cookies are pulled from the cache and added to current browser's context the current url
        # must be the same url where the cookies were retrieved. This is why the driver.get(url) call comes before
        # the self._setup_cookies call. _setup_cookies also validates the cookies
        if self.m_cache.is_cached(self.m_cookies_cache_key) and self._setup_cookies():
            print("Cookies were successfully retrieved from the cache and validated.")
            return
        # wait until email element is present
        _, error = self._wait_until("email")
        if error:
            print("[ERROR] Cannot recover from error during the login process. [{}]".format(error))
            raise error
        self.m_driver.find_element_by_id("email").send_keys(email)
        self.m_driver.find_element_by_id ("password").send_keys(password)
        self.m_driver.find_element_by_xpath("//button[@type='submit']").send_keys(Keys.ENTER)
        time.sleep(15) # pause this long incase there is a captcha
        self.m_cache[self.m_cookies_cache_key] = self.m_driver.get_cookies()

    def _process_urls(self, anchor_tags):
        urls = []    
        for a in anchor_tags:
            url = ""
            try:
                url = a.get_attribute("href")
            except StaleElementReferenceException as e:
                print("[ERROR] Failed to process anchor tag [{}] because [{}]".format(str(a), str(e)))
                continue
            url, valid = self._process_url(url)
            if valid:
                urls.append(url)
        return urls

    def _process_url(self, url: str):
        valid = True
        for rule in self.m_url_rules:
            valid &= rule(url=url)
        return url, valid

    def _process_page_content(self):
        text = self.m_driver.find_element(By.XPATH, "/html/body").text
        text = re.sub(self.m_page_content_regex, "", text)
        self.m_cache.update(self.m_page_content_cache_key, {self.m_driver.current_url : {self.m_page_text_cache_key : text} })

    def _scrape_urls(self, urls_to_scrape):
        for url in urls_to_scrape:
            if url in self.m_seen_urls:
                # if the url has been seen remove it
                if url in self.m_to_process_urls:
                    self.m_to_process_urls.remove(url)
                continue
            self.m_driver.get(url)
            # need to wait for page to fully load 
            print("Waiting for Page [{}]".format(url))

            # wait until all page links are loaded
            _, error = self._wait_until("//main[@id='main']", by=By.XPATH) # "rc-ModuleLessons", by=By.CLASS_NAME
            # just because the main div is visible doesn't mean its children are
            time.sleep(2)
            if error:
                print("[ERROR] Failed to load content for url [{}] because [{}]".format(url, error))
                continue
            urls = self._process_urls(self.m_driver.find_elements_by_xpath("//a[@href]"))
            print("Adding [{}] urls to be processed".format(len(urls)))

            # process page content
            self._process_page_content()

            # mark current url as seen and processed urls as to be processed
            self.m_seen_urls.add(url)
            self.m_to_process_urls.update(urls)

            # remove the current url from the to process set
            if url in self.m_to_process_urls:
                self.m_to_process_urls.remove(url)

            # save updated urls in cache file
            self.m_cache[self.m_seen_urls_cache_key] = list(self.m_seen_urls)
            self.m_cache[self.m_to_process_urls_cache_key] = list(self.m_to_process_urls)

    def run(self):
        self._login(self.m_email, self.m_password)
        self._scrape_urls(self._url_weeks())
        while self.m_to_process_urls:
            self._scrape_urls(list(self.m_to_process_urls))
        data = self.m_cache[self.m_page_content_cache_key]
        self._save_file(self.m_output_path, data)

    def quit(self):
        self.m_driver.quit()


# if __name__ == "__main__":
#     import settings
#     scraper = CouseraScraper(settings.COURSERA_URL, settings.COURSERA_EMAIL, settings.COURSERA_PASSWORD)
#     scraper.init_driver(settings.CHROME_DRIVER_PATH, headless=False)
#     scraper.run()
#     scraper.quit()