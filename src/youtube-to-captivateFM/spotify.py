import base64
import time

import requests

from configuration_manager import ConfigurationManager


def _get_spotify_access_token(client_id: str, client_secret: str) -> str:
    """
    Retrieve an access token from the Spotify API using the provided client ID and client secret.

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


def get_latest_spotify_episode_link(episode_name: str, podcast_channel_id: str, config: ConfigurationManager) -> str:
    """
    Retrieve the latest Spotify episode link for a given podcast channel and episode name using the provided access token.

    :param episode_name: The name of the episode to retrieve the link for.
    :type episode_name: str

    :param podcast_channel_id: The ID of the podcast channel to retrieve the link from.
    :type podcast_channel_id: str

    :param config: The config object with env secrets
    :type config: ConfigurationManager

    :return: The latest Spotify episode link for the given podcast channel and episode name.
    :rtype: str
    """
    access_token = _get_spotify_access_token(config.CLIENT_ID, config.CLIENT_SECRET)
    count = 5
    while count > 0:
        url = f"https://api.spotify.com/v1/shows/{podcast_channel_id}/episodes?market=us"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers).json()

        for i in range(5):
            episode = response["items"][i]
            if episode["name"] == episode_name:
                episode_link = episode["external_urls"]["spotify"]
                print(f"Found Spotify link for {episode_name}\n{episode_link}")
                return episode_link
        print(f"episode: {episode_name} not yet found on {podcast_channel_id}")
        count -= 1
        print("waiting 2 minutes to try again")
        time.sleep(120)
