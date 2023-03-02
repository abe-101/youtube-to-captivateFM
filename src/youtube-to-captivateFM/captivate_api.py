from datetime import datetime, time
from typing import Union

import requests

from configuration_manager import ConfigurationManager


def format_date(date_str: str) -> Union[str, None]:
    """
    This function takes in a date string in the format "YYYYMMDD" and returns it in the format "YYYY-MM-DD 12:00:00"


    :param date_str: The date string to be formatted
    :type date_str: str
    :return: The formatted date string
    :rtype: Union[str, None]
    """
    try:
        time_str = time(6, 30, 0)
        date_obj = datetime.strptime(date_str, "%Y%m%d").date()
        dt_obj = datetime.combine(date_obj, time_str)
        formatted_date = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_date

    except ValueError as e:
        print(e)
        return None


def upload_media(config: ConfigurationManager, show_id: str, file_name: str) -> Union[str, None]:
    """
    This function uploads a file to captivate.fm using an API, and returns the media_id.

    :param token: The API token to be used for authentication
    :type token: str
    :param show_id: The ID of the show's library you want your media to be uploaded in.
    :type show_id: str
    :param file_name: The name of the file to be uploaded
    :type file_name: str
    :return: The media_id of the uploaded file
    :rtype: Union[str, None]
    :raise: Exception if the file upload fails.
    """
    token = config.get_captivate_token()
    headers = {
        "Authorization": "Bearer " + token,
    }

    files = {
        "file": open(
            file_name,
            "rb",
        ),
    }

    try:
        response = requests.post(
            f"https://api.captivate.fm/shows/{show_id}/media",
            headers=headers,
            files=files,
        )
        response.raise_for_status()
        r = response.json()
        return r["media"]["id"]
    except requests.exceptions.HTTPError as error:
        print(f"An HTTP error occurred: {error}")
        return None


def create_podcast(
    config: ConfigurationManager,
    title: str,
    media_id: str,
    date: str,
    shownotes: str,
    shows_id: str,
    status: str = "draft",
    episode_season: str = "1",
    episode_number: str = "1",
) -> Union[str, None]:
    """
    This function creates a podcast on captivate.fm using the API, by taking in all the parameters and putting them in the payload, and returns the response.

    :param token: The API token to be used for authentication
    :type token: str
    :param title: The title of the episode
    :type title: str
    :param media_id: The media_id of the episode
    :type media_id: str
    :param date: The date of the episode
    :type date: str
    :param shownotes: The shownotes of the episode
    :type shownotes: str
    :param shows_id: The id of the show
    :type shows_id: str
    :param status: The status of the episode
    :type status: str
    :param episode_season: The season of the episode
    :type episode_season: str
    :param episode_number: The number of the episode
    :type episode_number: str

    """
    token = config.get_captivate_token()
    url = "https://api.captivate.fm/episodes"

    payload = {
        "shows_id": shows_id,
        "title": title,
        "media_id": media_id,
        "date": date,
        "status": status,
        "shownotes": shownotes,
        "episode_season": episode_season,
        "episode_number": episode_number,
    }

    files = []
    headers = {"Authorization": "Bearer " + token}

    try:
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        response.raise_for_status()
        r = response.json()
        episode_id = r["record"]["id"]

        return f"https://player.captivate.fm/episode/{episode_id}"
    except requests.exceptions.HTTPError as error:
        print(f"An HTTP error occurred: {error}")
        return None


def get_episode(config: ConfigurationManager, episode_id: str) -> Union[dict, None]:
    """
    This function gets the full information for a episode

    :param token: The API token to be used for authentication
    :type token: str
    :param episode_id: The id of the episode
    :type file_name: str
    :return: a dict with the episode info
    :rtype: Union[dict, None]
    :raise: Exception if the file upload fails.
    """
    token = config.get_captivate_token()
    url = f"https://api.captivate.fm/episodes/{episode_id}"
    headers = {
        "Authorization": "Bearer " + token,
    }

    payload = {}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()
        r = response.json()
        return r["episode"]
    except requests.exceptions.HTTPError as error:
        print(f"An HTTP error occurred: {error}")
        return None


def update_podcast(
    config: ConfigurationManager,
    media_id: str,
    shows_id: str,
    episode_id: str,
    shownotes: str,
    title: str,
    date: str,
    status: str = "draft",
    episode_season: str = "1",
    episode_number: str = "1",
) -> Union[str, None]:
    token = config.get_captivate_token()
    url = f"https://api.captivate.fm/episodes/{episode_id}"

    payload = {
        "shows_id": shows_id,
        "media_id": media_id,
        "title": title,
        "date": date,
        "status": status,
        "shownotes": shownotes,
        "episode_season": episode_season,
        "episode_number": episode_number,
    }

    files = []
    headers = {"Authorization": "Bearer " + token}

    try:
        response = requests.request("PUT", url, headers=headers, data=payload, files=files)
        response.raise_for_status()
        r = response.json()
        episode_id = r["episode"]["id"]

        return f"https://player.captivate.fm/episode/{episode_id}"
    except requests.exceptions.HTTPError as error:
        print(f"An HTTP error occurred: {error}")
        return None
