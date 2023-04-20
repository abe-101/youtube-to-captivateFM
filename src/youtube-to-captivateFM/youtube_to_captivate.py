#!/usr/bin/python

import asyncio
from datetime import datetime
import time

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
from podcast_links import get_episode_links, prepare_collive_post, prepare_sharable_post, prepare_collive_embed

load_dotenv()

config = ConfigurationManager()


def meseches_sota_shiur(youtube_url: str = None, file: str = None, title: str = None, picture: str = "sota.jpg"):
    description = """Looking for a comprehensive and in-depth study of Meseches Sota? Join Rabbi Shloimy Greenwald every day for a special 49-day learning program on this fascinating tractate.

Check out the Kolel L'Horaah Maasis channel for daily shiurim by Rabbi Shloimy Greenwald. Available on all major platforms, including:

YouTube - https://www.youtube.com/c/kolellhoraahmaasis

Apple Podcasts - https://podcasts.apple.com/us/podcast/kolel-lhoraah-maasis/id1670169956

Google Podcasts - https://podcasts.google.com/feed/aHR0cHM6Ly9hbmNob3IuZm0vcy85NTVlY2VjNC9wb2RjYXN0L3Jzcw

Spotify - https://open.spotify.com/show/7IfJEeqO8ZF1qCPKkW5DPE  
"""
    if youtube_url is not None:
        info = download_youtube_video(youtube_url, config.SOTA_DIR)
    else:
        info = {"file_name": file}
        if title is None:
            title = file.split("/")[-1].split(".")[0] + " - Rabbi Shloime Greenwald"
        info["title"] = title
        info["upload_date"] = datetime.now().strftime("%Y%m%d")

    if youtube_url is None:
        info["description"] = description

    #info["file_name"] = enhance_podcast(info["file_name"], config)
    info["thumbnail"] = picture
    upload_to_spotify_podcasters(info, config)
    if youtube_url is None:
        file = create_video_from_audio_and_picture(info["file_name"], picture, config.SOTA_DIR + title + ".mp4")
        print("Uploading to YouTube")
        upload_video_with_options(file, title, description=description, privacyStatus="public")

        youtube_url = input("What is the youtube link? ")
        print("======\n\n")

    #links = get_episode_links(title, config)
    #daf = "ח"
    youtube_id = youtube_url[-11:]
    col = prepare_collive_embed(title, youtube_id)
    #col = prepare_collive_post(links, daf, youtube_id)
    #post = prepare_sharable_post(links, daf, youtube_id)

   # with open(config.SOTA_DIR + "collection.csv", "a") as f:
   #     f.write(f"{title},{info['upload_date']},{youtube_url},{spotify_link}\n")
    return title, col


def likutei_torah_shiur(url: str):
    info = download_youtube_video(url, config.DATA_DIR)
    info["file_name"] = enhance_podcast(info["file_name"], config)
    info["upload_date"] = None
    info["url"] = None
    info["thumbnail"] = "shloimy.jpg"

    upload_to_spotify_podcasters(info, config)
    time.sleep(120)
    spotify_link = get_latest_spotify_episode_link(info["title"], config.KOLEL_SPOTIFY_ID, config)

    post_message = """
{title}

YouTube - {youtube}
Spotify - {spotify}
""".format(
        title=info["title"], youtube=info["url"], spotify=spotify_link
    )
    print(post_message)


def the_daily_halacha_shiur(file: str, title: str = None, desc: str = "", picture: str = "halacha.jpg"):
    if title is None:
        title = file.split("/")[-1].split(".")[0]

    description = (
        """Carpool Halacha

({title})
""".format(
            title=title
        )
        + desc
    )
    print(description)

    file = enhance_podcast(file, config)
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
    print("Uploading to YouTube")
    upload_video_with_options(file, title, description=description, privacyStatus="public")

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
    enhanced_file = enhance_podcast(combined, config)
    return enhanced_file


def download_combine_and_enhance(url: str, file: str) -> str:
    info = download_youtube_video(url, config.DATA_DIR)
    combined = combine_mp3_files(info["file_name"], file)
    enhanced_file = enhance_podcast(combined, config)
    return combined


def download_enhance_and_combine(url: str, file: str) -> str:
    info = download_youtube_video(url, config.DATA_DIR)
    enhanced_file = enhance_podcast(info["file_name"], config)
    combined = combine_mp3_files(file, enhanced_file)
    return combined


def download_and_enhance(url: str) -> str:
    info = download_youtube_video(url, config.DATA_DIR)
    enhanced_file = enhance_podcast(info["file_name"], config)
    return enhanced_file


def add_youtube_to_podcast(file_path_1, url, episode_id):
    info = download_youtube_video(url, config.DATA_DIR)
    file_path_2 = enhance_podcast(info["file_name"], config)
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


def add_audio_to_podcast(file_path_1, file_path_2, episode_id):
    #file_path_2 = enhance_podcast(file_path_2, config)
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

    title_2 = episode["title"] + " Part 2"

    file = create_video_from_audio_and_picture(file_path_2, "shloimy.jpg", title_2 + ".mp4")
    upload_video_with_options(file, title_2, description=episode["shownotes"], privacyStatus="public")


def pls_create_video_and_podcast(file: str, title: str, picture: str = "shloimy.jpg"):
    enhanced_file = enhance_podcast(file, config)

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
    #info["file_name"] = enhance_podcast(info["file_name"], config)
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
    print("\n\n")
    print(info["title"])
    print("YouTube - " + info["url"])
    print("Spotify - " + spotify_link)


# if __name__ == "__main__":
#    youtube_to_captivateFM(input("Enter url of youtube video: "))
