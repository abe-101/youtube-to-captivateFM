import base64
import requests
from typing import Dict, Any

def get_spotify_access_token(client_id: str, client_secret: str) -> str:
    """
    Fetches an access token from the Spotify API using a client ID and client secret.

    Parameters:
    client_id (str): The client ID for the Spotify API.
    client_secret (str): The client secret for the Spotify API.

    Returns:
    str: The access token for the Spotify API.
    """
    # Encode the client ID and client secret
    client_credentials = f'{client_id}:{client_secret}'
    encoded_credentials = base64.b64encode(client_credentials.encode('ascii')).decode('ascii')

    # Send a request to the Spotify API to fetch an access token
    url = 'https://accounts.spotify.com/api/token'
    headers = {'Authorization': f'Basic {encoded_credentials}'}
    data = {'grant_type': 'client_credentials'}
    response = requests.post(url, headers=headers, data=data)

    # Check if the request was successful
    if response.status_code != 200:
        raise ValueError('Failed to obtain Spotify access token')

    # Return the access token
    access_token = response.json()['access_token']
    return access_token


def get_latest_spotify_episode_link(podcast_channel: str, access_token: str) -> str:
    """
    Fetches the link of the latest episode of a podcast channel on Spotify.

    Parameters:
    podcast_channel (str): The name of the podcast channel.
    access_token (str): The access token for the Spotify API.

    Returns:
    str: The link of the latest episode of the podcast channel on Spotify.
    """
    url = f'https://api.spotify.com/v1/search?q={podcast_channel}&type=episode&limit=1'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers).json()

    # Check if any episodes were found
    if not response['episodes']['items']:
        raise ValueError(f'No episodes found for podcast channel: {podcast_channel}')

    # Return the link of the latest episode
    latest_episode = response['episodes']['items'][0]
    return latest_episode['external_urls']['spotify']

