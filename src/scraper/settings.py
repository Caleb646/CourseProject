from dotenv import load_dotenv, find_dotenv
import os

env_path = find_dotenv(raise_error_if_not_found=True)
assert env_path, "Could not find .env"
assert os.path.exists(env_path), "env_path does not exist."
load_dotenv(env_path)

CAMPUS_WIRE_API_URL = "https://api.campuswire.com/v1"
CAMPUS_WIRE_AUTH_TOKEN: str = os.environ["CAMPUS_WIRE_AUTH_TOKEN"]
CAMPUS_WIRE_GROUP_IDS: list[str] = os.environ["CAMPUS_WIRE_GROUP_IDS"].split(",")