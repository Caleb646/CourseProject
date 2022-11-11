# To Setup .env file
## The following two variables have to be placed in a .env file in the src/scraper directory. 
```
1. CAMPUS_WIRE_AUTH_TOKEN
  The auth token can be found with dev tools open while on Campuswire.
2. CAMPUS_WIRE_GROUP_IDS
  The Group Id for CS 410 can also be found in the dev tools.
3. COURSERA_EMAIL
  The email used to login to your Coursera account.
4. COURSERA_PASSWORD
  The password used to login to your Coursera account.
5. CHROME_DRIVER_PATH
  The path to the downloaded Selenium Webdriver for Chrome.
  The driver can be downloaded [here](https://chromedriver.chromium.org/downloads).
 ```
# To Run the Scrapers
## Inside the src/scraper directory
```
pip install -r requirements.txt
python main.py
```

# Campuswire Data
The already scraped posts can be found in the src/data/campuswire/group_id/ directory.

# Coursera Data
The already scraped posts can be found in the src/data/coursera/ directory.