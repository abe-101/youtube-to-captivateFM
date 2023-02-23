#!/usr/bin/python

import os

from dotenv import load_dotenv

from adobe_podcast import enhance_podcast
from audio_conversion import combine_mp3_files, create_video_from_audio_and_picture
from captivate_api import (
    create_podcast,
    format_date,
    get_episode,
    get_token,
    update_podcast,
    upload_media,
)
from download_yt import download_youtube_video
from upload_video import upload_video_with_options

load_dotenv()

USER_ID = os.getenv("USER_ID")
API_KEY = os.getenv("CAPTIVATE_API_KEY")
SHOW_ID = os.getenv("SHOWS_ID")
DATA_DIR = os.getenv("DATA_DIR")

daily_halacha = """Get your daily does of practical Halacha, in just 2 minutes.
The perfect and convenient way to start your day!
Shiur by Rabbi Shloimy Greenwald"""

def the_daily_halacha_shiur(file: str, picture: str, title: str, description=daily_halacha):
    print("Enhancing audio quality")
    file = enhance_podcast(file)
    print("Creating Video")
    file = create_video_from_audio_and_picture(file, picture, "data/halacha/" + title + ".mp4")
    print("Uploading to YouTube")
    upload_video_with_options(file, title, description, privacyStatus="public")


def download2_and_enhance(url1: str, url2: str) -> str:
    info1 = download_youtube_video(url1, DATA_DIR)
    file1 = info1["file_name"]
    print(file1)
    info2 = download_youtube_video(url1, DATA_DIR)
    file2 = info2["file_name"]
    print(file2)
    combined = combine_mp3_files(file1, file2)
    enhanced_file = enhance_podcast(combined)
    return enhanced_file


def download_and_enhance(url: str) -> str:
    info = download_youtube_video(url, DATA_DIR)
    print(info["file_name"])
    print("Enhancing audio quality")
    enhanced_file = enhance_podcast(info["file_name"])
    print(enhanced_file)
    return enhanced_file


def add_audio_to_podcast(file_path_1, url):
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


def temp_update(media_id, episode_id):
    token = get_token(user_id=USER_ID, api_key=API_KEY)
    episode_url = update_podcast(
        token=token,
        media_id=media_id,
        shows_id=SHOW_ID,
        episode_id=episode_id,
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
        shownotes=info["description"] + "\n" + url,
        shows_id=SHOW_ID,
    )
    print(episode_url)


if __name__ == "__main__":
    youtube_to_captivateFM(input("Enter url of youtube video: "))
