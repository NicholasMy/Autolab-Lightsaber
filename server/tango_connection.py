import requests


class TangoConnection:

    # This the old way we used to connect directly to Tango. Now we go through the Autolab Portal.

    def __init__(self, url: str, tango_api_key: str):
        # url should look like "http://something.buffalo.edu:1234"
        self.url = url
        self.tango_api_key = tango_api_key

    def get_current_jobs_count(self) -> int:
        try:
            url = f"{self.url}/jobs/{self.tango_api_key}/0/"
            res = requests.get(url)
            js = res.json()
            jobs_count = len(js["jobs"])
            return jobs_count

        except Exception as e:
            print("Error getting current jobs count: ", e)
            return -1
