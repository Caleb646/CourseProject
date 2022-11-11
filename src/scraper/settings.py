from dotenv import find_dotenv, load_dotenv
import os
env_path = find_dotenv(raise_error_if_not_found=True)
assert env_path, "Could not find .env"
assert os.path.exists(env_path), "env_path does not exist."
load_dotenv(env_path)

CAMPUS_WIRE_API_URL = "https://api.campuswire.com/v1"
CAMPUS_WIRE_AUTH_TOKEN = os.environ["CAMPUS_WIRE_AUTH_TOKEN"]
CAMPUS_WIRE_GROUP_IDS = os.environ["CAMPUS_WIRE_GROUP_IDS"].split(",")

CHROME_DRIVER_PATH = os.environ.get('CHROME_DRIVER_PATH', r'C:\\Users\\caleb\\Downloads\\chromedriver_win32 170\\chromedriver.exe')
COURSERA_URL = "https://www.coursera.org"
COURSERA_EMAIL = os.environ["COURSERA_EMAIL"]
COURSERA_PASSWORD = os.environ["COURSERA_PASSWORD"]