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

    def create_alias_url(self, long_url, alias, domain="tinyurl.com", tags=[], expires_at=""):
        payload = json.dumps(
            {"url": long_url, "domain": domain, "alias": alias, "tags": tags, "expires_at": expires_at}
        )

        response = requests.request("POST", self.url + "create", headers=self.headers, data=payload)
        return response.json()["data"]["tiny_url"]

    def get_alias_url(self, alias, domain="tinyurl.com"):
        response = requests.request("GET", self.url + f"alias/{domain}/{alias}", headers=self.headers)
        response_json = response.json()
        if "data" in response_json and response_json["data"]:
            return response_json["data"]["tiny_url"]
        else:
            return None

    def get_or_create_alias_url(self, long_url, alias, domain="tinyurl.com", tags=[], expires_at=""):
        if long_url == None:
            return None
        existing_url = self.get_alias_url(alias, domain)
        if existing_url:
            return existing_url
        else:
            return self.create_alias_url(long_url, alias, domain, tags, expires_at)



if "__main__" == __name__:
    # Example usage
    creator = TinyURLAPI(config.TINY_URL_API_KEY)
    youtube_url = creator.get_or_create_alias_url(
        "https://www.youtube.com/watch?v=57WTb6jNFqs",
        "VeAtah-Tetzaveh",
    )
    print(youtube_url)
    #youtube_url = creator.get_or_create_alias_url(
    #    "https://www.youtube.com/watch?v=U3omQ6aAYRc",
    #    "YouTube-Gittin-20",
    #)
    #print(youtube_url)
    #spotiy_url = creator.get_or_create_alias_url(
    #    "https://open.spotify.com/show/0Cgr6r1gTNNzbln8ghofjH",
    #    "Gittin-Spotify",
    #)
    #print(spotiy_url)
    #apple_url = creator.get_or_create_alias_url(
    #    "https://podcasts.apple.com/us/podcast/meseches-gittin-rabbi-shloime-greenwald/id1689640425",
    #    "Gittin-Apple",
    #)
    #print(apple_url)
    #print("\n\n")
    #print(youtube_url[8:])
    #print(spotiy_url[8:])
    #print(apple_url[8:])

