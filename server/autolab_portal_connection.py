from typing import Dict

import requests


class AutolabPortalConnection:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key

    def get_auth_headers(self):
        return {"Authorization": self.api_key}

    def get_tango_histogram(self) -> Dict[int, int]:
        url = f"{self.url}/api/user_api/tango_histogram/"
        res = requests.get(url, headers=self.get_auth_headers())
        str_dict = res.json()
        # The keys are strings. Convert them to ints.
        ret = {int(k): v for k, v in str_dict.items()}
        return ret
