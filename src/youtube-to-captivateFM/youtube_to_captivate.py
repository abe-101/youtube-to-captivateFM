#!/usr/bin/python

import asyncio
from datetime import datetime

from dotenv import load_dotenv

from adobe_podcast import enhance_podcast
from spotify_podcasters import upload_to_spotify_podcasters
from audio_conversion import (
    combine_mp3_files,
    combine_webm_files,
    create_video_from_audio_and_picture,
    convert_wav_to_mp3,
)
from captivate_api import create_podcast, format_date, get_episode, update_podcast, upload_media
from configuration_manager import ConfigurationManager
from download_yt import download_youtube_video
from spotify import get_latest_spotify_episode_link
from upload_video import upload_video_with_options

load_dotenv()

config = ConfigurationManager()


def likutei_torah_shiur(url: str):
    info = download_youtube_video(url, config.DATA_DIR)
    info["file_name"] = enhance_podcast(info["file_name"])
    asyncio.run(
        post_episode_anchorfm(
            info,
            config,
            URL_IN_DESCRIPTION=True,
            LOAD_THUMBNAIL="shloimy.jpg",
            SAVE_AS_DRAFT=False,
        )
    )
    spotify_link = get_latest_spotify_episode_link(info["title"], config.KOLEL_SPOTIFY_ID, config)

    post_message = """
{title}

YouTube - {youtube}
Spotify - {spotify}
""".format(
        title=info["title"], youtube=info["url"], spotify=spotify_link
    )
    print(post_message)


def the_daily_halacha_shiur(file: str, title: str, picture: str = "halacha.jpg"):
    description = """Carpool Halacha

({title})
The search and nullification of the Chametz 

Topics include 

- Proper time we check for Chametz 
- Which candle best to use 
- Where must one check
- Rooms sold to a goy do they require checking?
""".format(
        title=title
    )

    file = enhance_podcast(file)
    podcast_info = {
        "title": title,
        "description": description,
        "file_name": file,
        "upload_date": None,
        "url": None,
        "thumbnail": picture,
    }
    upload_to_spotify_podcasters(podcast_info, config)

    file = create_video_from_audio_and_picture(file, picture, "data/halacha/" + title + ".mp4")
    # print("Uploading to YouTube")
    # upload_video_with_options(file, title, description=daily_halacha, privacyStatus="public")

    print(description)
    youtube_link = input("What is the youtube link? ")
    print("======\n\n")
    spotify_link = get_latest_spotify_episode_link(title, config.KOLEL_SPOTIFY_ID, config)

    post_message = description + f"\nYouTube - {youtube_link}\nSpotify - {spotify_link}"
    print(post_message)


def download2_and_enhance(url1: str, url2: str) -> str:
    info1 = download_youtube_video(url1, config.DATA_DIR)
    file1 = info1["file_name"]
    info2 = download_youtube_video(url1, config.DATA_DIR)
    file2 = info2["file_name"]
    combined = combine_webm_files(file1, file2)
    enhanced_file = enhance_podcast(combined)
    return enhanced_file


def download_combine_and_enhance(url: str, file: str) -> str:
    info = download_youtube_video(url, config.DATA_DIR)
    combined = combine_mp3_files(info["file_name"], file)
    enhanced_file = enhance_podcast(combined)
    return combined


def download_enhance_and_combine(url: str, file: str) -> str:
    info = download_youtube_video(url, config.DATA_DIR)
    enhanced_file = enhance_podcast(info["file_name"])
    combined = combine_mp3_files(file, enhanced_file)
    return combined


def download_and_enhance(url: str) -> str:
    info = download_youtube_video(url, config.DATA_DIR)
    enhanced_file = enhance_podcast(info["file_name"])
    return enhanced_file


def add_audio_to_podcast(file_path_1, url, episode_id):
    info = download_youtube_video(url, config.DATA_DIR)
    file_path_2 = enhance_podcast(info["file_name"])
    combined = combine_mp3_files(file_path_1, file_path_2)
    media_id = upload_media(config=config, show_id=config.SHOWS_ID, file_name=combined)
    print(media_id)
    episode = get_episode(config, episode_id)
    episode_url = update_podcast(
        config=config,
        media_id=media_id,
        shows_id=config.SHOWS_ID,
        episode_id=episode_id,
        shownotes=episode["shownotes"],
        title=episode["title"],
        date=episode["published_date"],
        status=episode["status"],
        episode_season=episode["episode_season"],
        episode_number=episode["episode_number"],
    )

    print(episode_url)


def pls_create_video_and_podcast(file: str, title: str, picture: str = "shloimy.jpg"):
    enhanced_file = enhance_podcast(file)

    today = datetime.today()
    date_str = today.strftime("%Y%m%d")
    info = {
        "title": title,
        "description": title,
        "file_name": enhanced_file,
        "upload_date": date_str,
        "url": "",
    }
    audio_to_captivateFM(info)
    file = create_video_from_audio_and_picture(file, picture, "data/" + title + ".mp4")
    spotify_link = get_latest_spotify_episode_link(info["title"], config.PLS_SPOTIFY_ID, config)
    upload_video_with_options(file, title, description=info["description"], privacyStatus="public")


def youtube_to_captivateFM(url: str):
    info = download_youtube_video(url, config.DATA_DIR)
    info["file_name"] = enhance_podcast(info["file_name"])
    audio_to_captivateFM(info)


def audio_to_captivateFM(info):
    formatted_upload_date = format_date(info["upload_date"])
    media_id = upload_media(config=config, show_id=config.SHOWS_ID, file_name=info["file_name"])
    episode_url = create_podcast(
        config=config,
        media_id=media_id,
        date=formatted_upload_date,
        title=info["title"],
        shownotes=info["description"] + "\n" + info["url"],
        shows_id=config.SHOWS_ID,
    )
    spotify_link = get_latest_spotify_episode_link(info["title"], config.PLS_SPOTIFY_ID, config)
    print(episode_url)
    print(spotify_link)


# if __name__ == "__main__":
#    youtube_to_captivateFM(input("Enter url of youtube video: "))
