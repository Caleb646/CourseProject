import requests
import os
from pathlib import Path
import json
import time
from datetime import datetime, timedelta, timezone

class CampusWireScraper:
    BASE_OUTPUT_DIR = os.path.join(Path(__file__).resolve().parent, "data/campuswire/")
    def __init__(self, base_url: str, groups: list[str], 
                auth_token: str, request_interval: float = 0.5, 
                output_dir: str = BASE_OUTPUT_DIR, output: bool = False,
                posts_per_request: int = 50) -> None:
        assert groups and all(groups), groups # make sure groups is not empty and all groups are non-empty
        assert auth_token, auth_token
        assert base_url, base_url
        assert request_interval > 0.1, f"Request interval {{request_interval}} too low must be greater than 0.1."

        self.m_base_url = base_url
        self.m_group_ids = groups
        self.m_auth_token = auth_token
        self.m_request_interval = request_interval
        self.m_output_dir = output_dir
        self.m_output = output

        self.m_number_of_posts_per_query = posts_per_request
        self.m_headers = {"Authorization": f"Bearer {auth_token}"}

    def _url_posts_group(self, group_id, num_posts: int = None, before: str = None) -> str:
        if not num_posts:
            num_posts = self.m_number_of_posts_per_query
        if before:
            return f"{self.m_base_url}/group/{group_id}/posts?number={num_posts}&before={before}"
        return f"{self.m_base_url}/group/{group_id}/posts?number={num_posts}"

    def _url_messages_post(self, group_id: str, post_id: str) -> str:
        return f"{self.m_base_url}/group/{group_id}/posts/{post_id}/comments/"

    def _path_outfile(self, group_id, utc_now: datetime, date_to_str_format: str = '%m-%d-%YT%H-%M-%S') -> str:
        if not utc_now:
            utc_now = datetime.utcnow()
        return f"{self.m_output_dir}{group_id}/{utc_now.strftime(date_to_str_format)}.json"

    def _dt_to_cw_date_str(self, utc_now: datetime, sep: str = "T", ending: str = "Z") -> str:
        return utc_now.isoformat(sep=sep).split("+")[0] + ending

    def _get_posts_for_group(self, group_id: str, num_posts: int = None, before: str = None) -> dict:
        """
        list of posts = [{
            "id": "",
            "categoryId": "",
            "author": { .... },
            "title": "",
            "body": "",
        },]

        Image format in body: ![image.png](URL)
        Referencing another message format in the body: [#667](https://campuswire.com/c/GA6659058/feed/667)
        """
        url = self._url_posts_group(group_id, num_posts=num_posts, before=before)
        response = requests.get(url, headers=self.m_headers)
        assert response.status_code == 200, f"Reason: {response.reason} || URL: {url}"
        return response.json()

    def _get_all_messages_for_post(self, group_id: str, post_id: str) -> dict:
        """
        list of messages = {
            "id": "0b39713b-db0a-4b5b-86d5-940f6768a132",
            "author": { ... },
            "body": "",
        }

        Image format in body: ![image.png](URL)
        Referencing another message format in the body: [#667](https://campuswire.com/c/GA6659058/feed/667)
        """
        url = self._url_messages_post(group_id, post_id)
        response = requests.get(url, headers=self.m_headers)
        assert response.status_code == 200, f"Reason: {response.reason} || URL: {url}"
        return response.json()

    def _save(self, output_path: str, data: dict):
        _dir, _ = os.path.split(output_path)

        cur_dir = ""
        for p in os.path.normpath(_dir).split(os.sep):
            cur_dir += f"{p}/"
            if not os.path.exists(cur_dir):
                os.mkdir(cur_dir)
        data: str = json.dumps(data)
        with open(output_path, mode="w") as f:
            f.writelines(data)

    def _run(self, group_id: str, before: str = None):
        seen = set() # track post ids that have already been fetched
        try:
            all_posts_messages_by_group = {group_id : {} for group_id in self.m_group_ids}
            posts = self._get_posts_for_group(group_id, before=before)
            utc_now = datetime.now(tz=timezone.utc)
            if before:
                # convert UTC string to datetime object
                utc_now = datetime.strptime(before, '%Y-%m-%d %H:%M:%S.%f%z')
                # date has to be in this format or CampusWire's api will reject it
                before = self._dt_to_cw_date_str(utc_now)
                print(f"Using before [{before}]")
            while posts:
                for post in posts:
                    post_id = post["id"]
                    if post_id not in seen: # track already retrieved posts
                        post_title = post["title"]
                        messages = self._get_all_messages_for_post(group_id, post_id)
                        all_posts_messages_by_group[group_id][post_id] = {"post" : post, "messages" : messages}
                        seen.add(post_id)
                        print(f"Retrieved Messages for Post [{post_title}] with [{len(messages)}] messages. Before [{before}]")
                        time.sleep(self.m_request_interval)
                    
                utc_now = utc_now - timedelta(days=1)
                before = self._dt_to_cw_date_str(utc_now) # remove fraction # must look like "2022-10-22T20:36:13.412814Z"
                posts = self._get_posts_for_group(group_id, before=before)
            return all_posts_messages_by_group, utc_now, None
        except Exception as e:
            self._save(self._path_outfile(group_id, utc_now), all_posts_messages_by_group)
            self._save(f"{self.m_output_dir}{group_id}/Last Before TimeStamp.json", {"before" : str(utc_now)})
            print(f"Exception encountered [{e.with_traceback()}]")
            return all_posts_messages_by_group, utc_now, e

    def scrape(self, before: str = None):
        # format: group_id -> post_id -> {post, messages}
        all_posts_messages_by_group = {group_id : {} for group_id in self.m_group_ids}
        for group_id in self.m_group_ids:
            posts, utc_now, exception = self._run(group_id, before)
            if exception: # try to recover from exception
                time.sleep(3)
                posts, utc_now, exception = self._run(group_id, str(utc_now))
                if exception: # if another exception is encountered reraise it
                    print(f"Ended with before of [{utc_now}]")
                    raise exception
            all_posts_messages_by_group.update(posts)
            self._save(self._path_outfile(group_id, utc_now), all_posts_messages_by_group)
            all_posts_messages_by_group.clear()
    