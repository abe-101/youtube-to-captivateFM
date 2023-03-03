import os
import base64
import requests
from typing import Union


class ConfigurationManager:
    def __init__(self):
        self.CAPTIVATE_USER_ID = os.getenv("CAPTIVATE_USER_ID")
        self.CAPTIVATE_API_KEY = os.getenv("CAPTIVATE_API_KEY")
        self.SHOWS_ID = os.getenv("SHOWS_ID")
        self.DATA_DIR = os.getenv("DATA_DIR")
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.KOLEL_SPOTIFY_ID = os.getenv("KOLEL_SPOTIFY_ID")
        self.PLS_SPOTIFY_ID = os.getenv("PLS_SPOTIFY_ID")
        self.ANCHOR_EMAIL = os.getenv("ANCHOR_EMAIL")
        self.ANCHOR_PASSWORD = os.getenv("ANCHOR_PASSWORD")
        self.PUPETEER_HEADLESS = os.getenv("PUPETEER_HEADLESS")
        self.CAPTIVATE_TOKEN = None
        self.SPOTIFY_TOKEN = None

    def get_captivate_token(self):
        if self.CAPTIVATE_TOKEN is None:
            # Get the Captivate token
            print("Getting captivate token from api")
            self.CAPTIVATE_TOKEN = self._get_captivate_token()
        return self.CAPTIVATE_TOKEN

    def _get_captivate_token(self) -> Union[str, None]:
        """
        This function gets a token from the captivate.fm API, using the user_id and api_key as authentication.

        :param user_id: The user_id of the account to get a token for
        :type user_id: str
        :param api_key: The api_key for the account
        :type api_key: str
        :return: The token from the API
        :rtype: Union[str, None]
        :raise: Exception if the API request fails.
        """
        url = "https://api.captivate.fm/authenticate/token"

        payload = {"username": self.CAPTIVATE_USER_ID, "token": self.CAPTIVATE_API_KEY}
        files = []
        headers = {}

        try:
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            response.raise_for_status()
            r = response.json()
            return r["user"]["token"]
        except requests.exceptions.HTTPError as error:
            print(f"An HTTP error occurred: {error}")
            return

    def get_spotify_token(self):
        if not self.SPOTIFY_TOKEN:
            self.SPOTIFY_TOKEN = self._get_spotify_access_token(self.CLIENT_ID, self.CLIENT_SECRET)
        return self.SPOTIFY_TOKEN

    def _get_spotify_access_token(self, client_id: str, client_secret: str) -> str:
        """
        Retrieve an access token from the Spotify API using the provided client ID
        and client secret.

        :param client_id: The client ID for the Spotify API.
        :type client_id: str

        :param client_secret: The client secret for the Spotify API.
        :type client_secret: str

        :return: The access token for the Spotify API.
        :rtype: str
        """

        # Encode the client ID and client secret
        client_credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(client_credentials.encode("ascii")).decode("ascii")

        # Send a request to the Spotify API to fetch an access token
        url = "https://accounts.spotify.com/api/token"
        headers = {"Authorization": f"Basic {encoded_credentials}"}
        data = {"grant_type": "client_credentials"}
        response = requests.post(url, headers=headers, data=data)

        # Check if the request was successful
        if response.status_code != 200:
            raise ValueError("Failed to obtain Spotify access token")

        # Return the access token
        access_token = response.json()["access_token"]
        return access_token
