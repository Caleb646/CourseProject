import unittest

from .test_courserascraper import TestCourseraScraper 
from .test_basescraper import TestBaseScraper, TestCache


scraper_test_suite = unittest.TestSuite()
scraper_test_suite.addTest(unittest.makeSuite(TestCourseraScraper))
scraper_test_suite.addTest(unittest.makeSuite(TestBaseScraper))
scraper_test_suite.addTest(unittest.makeSuite(TestCache))