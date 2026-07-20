import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("JIRA_URL")
session = requests.Session()

session.headers.update({
    "Authorization": f"Bearer {os.getenv('JIRA_TOKEN')}",
    "Content-Type": "application/json",
    "Accept": "application/json"
})


class JiraClient:

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url.rstrip("/")

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        while True:
            response = self.session.request(method, url, **kwargs)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                try:
                    wait = int(retry_after)
                except (TypeError, ValueError):
                    wait = 60
                print(f"Rate limit reached (HTTP 429). Waiting {wait} seconds...")
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response
