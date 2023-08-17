import json
from urllib.parse import urlparse

import requests
from configuration_manager import ConfigurationManager
from dotenv import load_dotenv

load_dotenv()

config = ConfigurationManager()


def capitalize_url(url):
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split(".")
    capitalized_domain = ".".join(
        [part.capitalize() if i < len(domain_parts) - 1 else part for i, part in enumerate(domain_parts)]
    )
    capitalized_url = f"{parsed_url.scheme}://{capitalized_domain}{parsed_url.path}"
    return capitalized_url


class TinyURLAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.url = "https://api.tinyurl.com/"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }

    def create_alias_url(self, long_url, alias, domain="my.shiurim.net", tags="", expires_at=""):
        if tags == "":
            tags = []
        payload = json.dumps(
            {"url": long_url, "domain": domain, "alias": alias, "tags": tags, "expires_at": expires_at}
        )

        response = requests.request("POST", self.url + "create", headers=self.headers, data=payload)
        return capitalize_url(response.json()["data"]["tiny_url"])

    def get_alias_url(self, alias, domain="my.shiurim.net"):
        response = requests.request("GET", self.url + f"alias/{domain}/{alias}", headers=self.headers)
        response_json = response.json()
        if "data" in response_json and response_json["data"]:
            return capitalize_url(response_json["data"]["tiny_url"])
        else:
            return None

    def get_or_create_alias_url(self, long_url, alias, domain="my.shiurim.net", tags="", expires_at=""):
        if tags == "":
            tags = []
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
    url = creator.get_or_create_alias_url(
        "https://podcasts.apple.com/us/podcast/meseches-kidushin-rabbi-shloimy-greenwald/id1702973020",
        "Kidushin-Apple",
    )
    print(url)

    url = creator.get_or_create_alias_url(
        "https://open.spotify.com/show/47DILD7zgofUlxttgXG1RQ",
        "Kidushin-Spotify",
    )
    print(url)
#    url = creator.get_or_create_alias_url(
#        "https://podcasts.google.com/feed/aHR0cHM6Ly9mZWVkcy5jYXB0aXZhdGUuZm0vZ2l0dGlu",
#        "Kidushin-Google",
#    )
#    print(url)
    url = creator.get_or_create_alias_url(
        "https://www.youtube.com/playlist?list=PLFy3gCT2Rdy-B3O9QSkvJCzM1pHLSIbCs'",
        "Kidushin-YouTube",
    )
    print(url)
    url = creator.get_or_create_alias_url(
        "https://gittin.captivate.fm/listen",
        "Kidushin",
    )
    print(url)
