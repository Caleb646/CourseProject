import unittest
import os

from .test_settings import TEST_DIR, CACHE_FNAME, CACHE_PATH
import scrapers.coursera as c  

# invalid urls contain the words quiz, exam, #tag_name, and don't contain www.coursera.org and cs-410
invalid_urls = [
    "https://www.coursera.org/learn/cs-410/exam/E81Mz/orientation-quiz", 
    "https://www.coursera.org/learn/cs-410/quiz/bAk3a/week-3-practice-quiz", 
    "https://www.coursera.org/learn/cs-410/home/week/15#main", 
    "https://www.coursera.org/learn/cs-410/exam/PaNAP/week-8-quiz", 
    "https://www.coursera.org/learn/cs-410/lecture/7hOfP/12-8-summary-for-exam-2", 
    "https://www.coursera.org/learn/cs-410/exam/S0Bpp/week-11-quiz", 
    "https://www.coursera.org/learn/cs-410/quiz/GYBV8/pre-quiz", 
    "https://www.coursera.org/learn/cs-410/home/week/10#main", 
    "https://www.coursera.org/learn/cs-410/home/week/5#main", 
    "https://www.coursera.org/learn/cs-410/quiz/CTsPR/week-6-practice-quiz",
    "https://www.coursera.org/learn/cs-410/home/week/11#main", 
    "https://www.coursera.org/my-purchases", 
    "https://www.coursera.org/learn/cs-410/supplement/dE9Wb/how-to-use-proctoru-for-exams", 
    "https://www.coursera.org/"
    ]

valid_urls = [
    "https://www.coursera.org/learn/cs-410/E81Mz/", 
    "https://www.coursera.org/learn/cs-410/bAk3a/week-3", 
    "https://www.coursera.org/learn/cs-410/home/week/15", 
    "https://www.coursera.org/learn/cs-410/PaNAP/week-8-", 
    "https://www.coursera.org/learn/cs-410/lecture/7hOfP/12-8-summary-for--2", 
    "https://www.coursera.org/learn/cs-410/S0Bpp/week-11-", 
    "https://www.coursera.org/learn/cs-410/GYBV8/pre-", 
    "https://www.coursera.org/learn/cs-410/home/week/10main", 
    "https://www.coursera.org/learn/cs-410/home/week/5main", 
    "https://www.coursera.org/learn/cs-410/CTsPR/week-6-practice-",
    "https://www.coursera.org/learn/cs-410/home/week/11main", 
    "https://www.coursera.org/learn/cs-410/supplement/dE9Wb/how-to-use-proctoru-for-s", 
    ]

class TestCourseraScraper(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.url = "https://test/test/test/test"
        self.output_dir = TEST_DIR
        self.email = "test@email.com"
        self.password = "12345"
        self.scraper = c.CouseraScraper(self.url, self.email, self.password, output_dir=self.output_dir)

    def test_init(self):
        self.assertEqual(self.url, self.scraper.m_base_url)

        self.assertEqual(self.email, self.scraper.m_email)

        self.assertEqual(self.password, self.scraper.m_password)

        self.assertEqual(self.output_dir, self.scraper.m_output_dir)

    def test_url_rules_w_invalid_urls(self):
        res = []
        for url in invalid_urls:
            url, valid = self.scraper._process_url(url)
            if valid:
                res.append(url)
        self.assertEqual(len(res), 0)

    def test_url_rules_w_valid_urls(self):
        res = []
        for url in valid_urls:
            url, valid = self.scraper._process_url(url)
            if valid:
                res.append(url)
        self.assertEqual(len(res), len(valid_urls))
