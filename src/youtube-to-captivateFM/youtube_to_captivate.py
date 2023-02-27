#!/usr/bin/python

import os
import asyncio

from dotenv import load_dotenv

from adobe_podcast import enhance_podcast
from audio_conversion import combine_mp3_files, create_video_from_audio_and_picture, combine_webm_files
from captivate_api import (
    create_podcast,
    format_date,
    get_episode,
    get_token,
    update_podcast,
    upload_media,
)
from download_yt import download_youtube_video
from spotify import get_spotify_access_token, get_latest_spotify_episode_link
from upload_video import upload_video_with_options
from anchorFM import post_episode_anchorfm

load_dotenv()

USER_ID = os.getenv("USER_ID")
API_KEY = os.getenv("CAPTIVATE_API_KEY")
SHOW_ID = os.getenv("SHOWS_ID")
DATA_DIR = os.getenv("DATA_DIR")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_CHANNEL_ID = os.getenv("SPOTIFY_CHANNEL_ID")
ANCHOR_EMAIL = os.getenv("ANCHOR_EMAIL")
ANCHOR_PASSWORD = os.getenv("ANCHOR_PASSWORD")


def get_spotify_link_for_podcast(podcast_name: str):
    access_token = get_spotify_access_token(CLIENT_ID, CLIENT_SECRET)
    link = get_latest_spotify_episode_link(podcast_name, SPOTIFY_CHANNEL_ID, access_token)
    return link


def likutei_torah_shiur(url: str):
    info = download_youtube_video(url, DATA_DIR)
    print(info["file_name"])
    print("Enhancing audio quality")
    info["file_name"] = enhance_podcast(info["file_name"])

    asyncio.run(
        post_episode_anchorfm(
            info,
            ANCHOR_EMAIL,
            ANCHOR_PASSWORD,
            PUPETEER_HEADLESS=False,
            URL_IN_DESCRIPTION=False,
            LOAD_THUMBNAIL="shloimy.jpg",
            SAVE_AS_DRAFT=False,
        )
    )
    spotify_link = get_spotify_link_for_podcast(info["title"])

    post_message = """
{title}

youtube - {youtube}
spotify - {spotify}
""".format(
        title=info["title"], youtube=youtube_link, spotify=spotify_link
    )
    print(post_message)


def the_daily_halacha_shiur(file: str, title: str, picture: str = "halacha.jpg"):
    daily_halacha = """Get your daily dose of practical Halacha, in just 2 minutes.
    The perfect and convenient way to start your day!
    Shiur by Rabbi Shloimy Greenwald"""
    print("Enhancing audio quality")
    file = enhance_podcast(file)
    podcast_info = {
        "title": title,
        "description": daily_halacha,
        "file_name": file,
        "upload_date": None,
        "url": None,
    }
    asyncio.run(
        post_episode_anchorfm(
            podcast_info,
            ANCHOR_EMAIL,
            ANCHOR_PASSWORD,
            PUPETEER_HEADLESS=False,
            URL_IN_DESCRIPTION=False,
            LOAD_THUMBNAIL=picture,
            SAVE_AS_DRAFT=False,
        )
    )

    print("Creating Video")
    file = create_video_from_audio_and_picture(file, picture, "data/halacha/" + title + ".mp4")
    # print("Uploading to YouTube")
    # upload_video_with_options(file, title, description=daily_halacha, privacyStatus="public")

    youtube_link = input("What is the youtube link? ")
    print("======\n\n")
    spotify_link = get_spotify_link_for_podcast(title)

    post_message = """
Carpool Halacha

*The Laws of reading the Megillah*
({title})
Topics include:

- Carrying a Megillah on Shabbos even with an Eriv
- If theirs no Kosher Megillah in the Shul, or no one knows how to sing the trop properly,what should be done.
- If a Megillah is missing words or sections what’s the proper conduct.

youtube - {youtube}
spotify - {spotify}
""".format(
        title=title, youtube=youtube_link, spotify=spotify_link
    )
    print(post_message)


def download2_and_enhance(url1: str, url2: str) -> str:
    info1 = download_youtube_video(url1, DATA_DIR)
    file1 = info1["file_name"]
    print(file1)
    info2 = download_youtube_video(url1, DATA_DIR)
    file2 = info2["file_name"]
    print(file2)
    combined = combine_webm_files(file1, file2)
    enhanced_file = enhance_podcast(combined)
    return enhanced_file


def download_and_enhance(url: str) -> str:
    info = download_youtube_video(url, DATA_DIR)
    print(info["file_name"])
    print("Enhancing audio quality")
    enhanced_file = enhance_podcast(info["file_name"])
    print(enhanced_file)
    return enhanced_file


def add_audio_to_podcast(file_path_1, url, episode_id):
    info = download_youtube_video(url, DATA_DIR)
    print("Enhancing audio quality")
    file_path_2 = enhance_podcast(info["file_name"])
    print("Combining audio files")
    combined = combine_mp3_files(file_path_1, file_path_2)
    print("getting user token")
    token = get_token(user_id=USER_ID, api_key=API_KEY)
    print("uploading media: " + combined)
    media_id = upload_media(token=token, show_id=SHOW_ID, file_name=combined)
    print(media_id)
    episode = get_episode(token, episode_id)
    episode_url = update_podcast(
        token=token,
        media_id=media_id,
        shows_id=SHOW_ID,
        episode_id=episode_id,
        shownotes=episode["shownotes"],
        title=episode["title"],
        date=episode["published_date"],
        status=episode["status"],
        episode_season=episode["episode_season"],
        episode_number=episode["episode_number"],
    )
    print(episode_url)


def youtube_to_captivateFM(url: str):
    info = download_youtube_video(url, DATA_DIR)
    formatted_upload_date = format_date(info["upload_date"])
    print(info["file_name"])
    print("Enhancing audio quality")
    enhanced_file = enhance_podcast(info["file_name"])
    print(enhanced_file)
    print("getting user token")
    token = get_token(user_id=USER_ID, api_key=API_KEY)
    print("uploading media: " + enhanced_file)
    media_id = upload_media(token=token, show_id=SHOW_ID, file_name=enhanced_file)
    print("creating podcast")
    episode_url = create_podcast(
        token=token,
        media_id=media_id,
        date=formatted_upload_date,
        title=info["title"],
        shownotes=info["description"] + "\n" + info["url"],
        shows_id=SHOW_ID,
    )
    print(episode_url)


if __name__ == "__main__":
    youtube_to_captivateFM(input("Enter url of youtube video: "))
