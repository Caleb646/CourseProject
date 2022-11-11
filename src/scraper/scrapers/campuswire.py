import requests
import os
import json
import time
from datetime import datetime, timedelta, timezone

from .basescraper import BaseScraper, DEFAULT_DATA_DIR

class CampusWireScraper:
    DEFAULT_DATA_DIR = os.path.join(DEFAULT_DATA_DIR, "campuswire/")
    def __init__(self, base_url, groups, 
                auth_token, request_interval: float = 0.5, 
                output_dir = DEFAULT_DATA_DIR, output: bool = False,
                posts_per_request = 50) -> None:
        assert groups and all(groups), groups # make sure groups is not empty and all groups are non-empty
        assert auth_token, auth_token
        assert base_url, base_url
        assert request_interval > 0.1, "Request interval [{}] too low must be greater than 0.1.".format(request_interval)

        self.m_base_url = base_url
        self.m_group_ids = groups
        self.m_auth_token = auth_token
        self.m_request_interval = request_interval
        self.m_output_dir = output_dir
        self.m_output = output

        self.m_number_of_posts_per_query = posts_per_request
        self.m_headers = {"Authorization": "Bearer {}".format(auth_token)}

    def _url_posts_group(self, group_id, num_posts = None, before = None):
        if not num_posts:
            num_posts = self.m_number_of_posts_per_query
        if before:
            return "{}/group/{}/posts?number={}&before={}".format(self.m_base_url, group_id, num_posts, before)
        return "{}/group/{}/posts?number={}".format(self.m_base_url, group_id, num_posts)

    def _url_messages_post(self, group_id, post_id):
        return "{}/group/{}/posts/{}/comments/".format(self.m_base_url, group_id, post_id)

    def _path_outfile(self, group_id, utc_now, date_to_str_format = '%m-%d-%YT%H-%M-%S'):
        if not utc_now:
            utc_now = datetime.utcnow()
        return "{}{}/{}.json".format(self.m_output_dir, group_id, utc_now.strftime(date_to_str_format))

    def _dt_to_cw_date_str(self, utc_now, sep = "T", ending = "Z"):
        return utc_now.isoformat(sep=sep).split("+")[0] + ending

    def _get_posts_for_group(self, group_id, num_posts = None, before = None):
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
        assert response.status_code == 200, "Reason: {} || URL: {}".format(response.reason, url)
        return response.json()

    def _get_all_messages_for_post(self, group_id, post_id):
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
        assert response.status_code == 200, "Reason: {} || URL: {}".format(response.reason, url)
        return response.json()

    def _save(self, output_path, data):
        _dir, _ = os.path.split(output_path)
        os.makedirs(_dir, exist_ok=True)
        data = json.dumps(data)
        with open(output_path, mode="w") as f:
            f.writelines(data)

    def _run(self, group_id, before = None):
        seen = set() # track post ids that have already been fetched
        utc_now = datetime.now(tz=timezone.utc)
        try:
            all_posts_messages_by_group = {group_id : {} for group_id in self.m_group_ids}
            posts = self._get_posts_for_group(group_id, before=before)
            if before:
                # convert UTC string to datetime object
                utc_now = datetime.strptime(before, '%Y-%m-%d %H:%M:%S.%f%z')
                # date has to be in this format or CampusWire's api will reject it
                before = self._dt_to_cw_date_str(utc_now)
                print("Using before [{}]".format(before))
            while posts:
                for post in posts:
                    post_id = post["id"]
                    if post_id not in seen: # track already retrieved posts
                        post_title = str(post["title"]).encode("utf-8")
                        messages = self._get_all_messages_for_post(group_id, post_id)
                        all_posts_messages_by_group[group_id][post_id] = {"post" : post, "messages" : messages}
                        seen.add(post_id)
                        print("Retrieved Messages for Post [{}] with [{}] messages. Before [{}]".format(post_title, len(messages), str(before).encode("utf-8")))
                        time.sleep(self.m_request_interval)
                    
                utc_now = utc_now - timedelta(days=1)
                before = self._dt_to_cw_date_str(utc_now) # remove fraction # must look like "2022-10-22T20:36:13.412814Z"
                posts = self._get_posts_for_group(group_id, before=before)
            return all_posts_messages_by_group, utc_now, None
        except Exception as e:
            print("Exception encountered [{}]".format(str(e)))
            return all_posts_messages_by_group, utc_now, e

    def scrape(self, before = None):
        # format: group_id -> post_id -> {post, messages}
        all_posts_messages_by_group = {group_id : {} for group_id in self.m_group_ids}
        for group_id in self.m_group_ids:
            posts, utc_now, exception = self._run(group_id, before)
            all_posts_messages_by_group.update(posts) # save posts
            if exception: # try to recover from exception
                time.sleep(5)
                posts, utc_now, exception = self._run(group_id, str(utc_now))
                all_posts_messages_by_group.update(posts)
                if exception: # if another exception is encountered reraise it
                    print("Ended with before of [{}]".format(utc_now))
                    self._save(self._path_outfile(group_id, utc_now), all_posts_messages_by_group)
                    self._save("{}{}/Last Before TimeStamp.json".format(self.m_output_dir, group_id), {"before" : str(utc_now)})
                    raise exception
            self._save(self._path_outfile(group_id, utc_now), all_posts_messages_by_group)
            all_posts_messages_by_group.clear()
    