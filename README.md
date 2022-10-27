# Intelligent Browsing

The purpose of this project is to allow a user, in one place, to search for content across Campuswire and Coursera content.


# To Setup .env file
## The following two variables have to be placed in a .env file in the src/scraper directory. 
```
1. CAMPUS_WIRE_AUTH_TOKEN
  The auth token can be found with dev tools open while on Campuswire.
2. CAMPUS_WIRE_GROUP_IDS
  The Group Id for CS 410 can also be found in the dev tools.
 ```

# To Run
## Inside the src/scraper directory
```
pip install -r requirements.txt
python main.py
```

# Campuswire Posts
The already scraped posts can be found in the src/data/campuswire/group_id/ directory.