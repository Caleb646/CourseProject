import unittest

from tests.tests import scraper_test_suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(scraper_test_suite)