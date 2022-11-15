from scrapers.campuswire import CampusWireScraper
from scrapers.coursera import CouseraScraper

from multiprocessing import Process
import json

def run_campuswire(url, group_ids, auth_token):
    scraper = CampusWireScraper(url, group_ids, auth_token) 
    scraper.scrape()

def run_coursera(url, email, password, chrome_path):
    scraper = CouseraScraper(url, email, password)
    # NOTE when first starting the scraper it should be ran with headless=False.
    scraper.init_driver(chrome_path, headless=False)
    scraper.run()

if __name__ == "__main__":
    import settings
    
    cw_url = settings.CAMPUS_WIRE_API_URL
    cw_group_ids = settings.CAMPUS_WIRE_GROUP_IDS
    cw_auth_token = settings.CAMPUS_WIRE_AUTH_TOKEN

    c_url = settings.COURSERA_URL
    c_email = settings.COURSERA_EMAIL
    c_password = settings.COURSERA_PASSWORD
    c_chrome_path = settings.CHROME_DRIVER_PATH

    p1 = Process(target=run_campuswire, args=(cw_url, cw_group_ids, cw_auth_token))
    p2 = Process(target=run_coursera, args=(c_url, c_email, c_password, c_chrome_path))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
