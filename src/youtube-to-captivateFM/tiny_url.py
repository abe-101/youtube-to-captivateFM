import requests
import json
from dotenv import load_dotenv
from configuration_manager import ConfigurationManager

load_dotenv()

config = ConfigurationManager()


class TinyURLAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.url = "https://api.tinyurl.com/"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }

    def create_short_url(self, long_url, alias, domain="tinyurl.com", tags=[], expires_at=""):
        payload = json.dumps(
            {"url": long_url, "domain": domain, "alias": alias, "tags": tags, "expires_at": expires_at}
        )

        response = requests.request("POST", self.url + "create", headers=self.headers, data=payload)
        return response.json()["data"]["tiny_url"]


# Example usage
creator = TinyURLAPI(config.TINY_URL_API_KEY)
apple_url = creator.create_short_url(
    "https://podcasts.apple.com/us/podcast/kitzur-shulchan-aruch-%D7%A7%D7%A9%D7%95-%D7%A2-%D7%A1%D7%99%D7%9E%D7%9F-%D7%97-%D7%94%D7%9C%D7%9B%D7%95%D7%AA-%D7%93-%D7%95/id1684880937?i=1000614142250",
    "Kitzur-5-23-Apple",
)

print(apple_url)
youtube_url = creator.create_short_url(
    "https://www.youtube.com/watch?v=QeovTCogC8M",
    "Kitzur-5-23-YouTube",
)

spotiy_url = creator.create_short_url(
    "https://open.spotify.com/episode/0V1p1cqEmyRje4oaJWxhze",
    "Kitzur-5-23-Spotiy",
)
print(spotiy_url)
