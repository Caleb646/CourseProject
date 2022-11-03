import settings
from campuswire import CampusWireScraper
import json


if __name__ == "__main__":

    scraper = CampusWireScraper(settings.CAMPUS_WIRE_API_URL, settings.CAMPUS_WIRE_GROUP_IDS, settings.CAMPUS_WIRE_AUTH_TOKEN) 
    #scraper.scrape()

    data_path = r"C:/Users/caleb/Coding Projects/CS 410 Projects/Final Project/src/scraper/data/campuswire/984118d3-29f1-4a34-9a3b-14c65608f28c/08-19-2022T14-52-49.json"

    with open(data_path, mode="r") as f:
        data = json.load(f)
        for group_id, posts, in data.items():
            print(len(posts))
