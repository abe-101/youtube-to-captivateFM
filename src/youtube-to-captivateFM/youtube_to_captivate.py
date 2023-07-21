#!/usr/bin/python

import asyncio
import time
from datetime import datetime

from dotenv import load_dotenv
from imgurpython import ImgurClient

from adobe_podcast import enhance_podcast
from audio_conversion import (
    combine_mp3_files,
    combine_webm_files,
    convert_wav_to_mp3,
    create_video_from_audio_and_picture,
)
from captivate_api import create_podcast, format_date, get_episode, publish_podcast, update_podcast, upload_media
from configuration_manager import ConfigurationManager, LocalMedia
from download_yt import download_youtube_video
from spotify import get_latest_spotify_episode_link
from upload_video import upload_video_with_options
import logging

# Set up logging configuration
logging.basicConfig(
    filename="log_file.log", level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get a logger instance for the current module
logger = logging.getLogger(__name__)


load_dotenv()

config = ConfigurationManager()


def all_kolel():
    with open("needs_podcasts.csv") as f:
        for line in f:
            kolel(line[:11])


def kolel(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.kolel["dir"], logger)
    print(local_media)
    episode = publish_podcast(local_media, config.kolel, config, logger)
    return episode


def shuchat_podcast(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.shuchat["dir"], logger=logger)
    episode = publish_podcast(local_media, config.shuchat, config, logger=logger)
    return episode


def gittin_audio_podcast(file: str, title: str = None, desc: str = "", picture: str = "gittin.jpg"):
    if title is None:
        title = file.split("/")[-1].split(".")[0]
    file = enhance_podcast(file, config, logger)
    num_daf = "".join([char for char in title if char.isdigit()])
    local_media = LocalMedia(file_name=file, title=title, description=title + "\n" + desc, thumbnail=picture)
    try:
        print("getting thumbnail")
        client = ImgurClient(config.IMGUR_CLIENT_ID, config.IMGUR_CLIENT_SECRET)
        pic = config.gittin["dir"] + "/podcast/square/" + num_daf + ".jpg"
        print(pic)
        uploaded_image = client.upload_from_path(pic)
        print(uploaded_image["link"])
        local_media.thumbnail = uploaded_image["link"]
    except Exception as e:
        print("Error occurred during image uploading:", str(e))
        # Handle the error or take appropriate action here

    #episode = publish_podcast(local_media, config.gittin, config, episode_num=str(num_daf), logger=logger)

    videoPic = config.gittin["dir"] + "/youtube/YouTube/" + num_daf + ".jpg"
    local_media.file_name = create_video_from_audio_and_picture(file, videoPic, "data/gittin/" + title + ".mp4")
    print("Uploading to YouTube")
    youtube_url = upload_video_with_options(local_media, privacyStatus="public")


def meseches_gittin_shiur(youtube_url: str):
    local_media: LocalMedia = download_youtube_video(youtube_url, config.gittin["dir"], logger=logger)
    num_daf = "".join([char for char in local_media.title if char.isdigit()])

    try:
        print("getting thumbnail")
        client = ImgurClient(config.IMGUR_CLIENT_ID, config.IMGUR_CLIENT_SECRET)
        pic = config.gittin["dir"] + "/podcast/square/" + num_daf + ".jpg"
        print(pic)
        uploaded_image = client.upload_from_path(pic)
        print(uploaded_image["link"])
        local_media.thumbnail = uploaded_image["link"]
    except Exception as e:
        print("Error occurred during image uploading:", str(e))
        # Handle the error or take appropriate action here

    episode = publish_podcast(local_media, config.gittin, config, episode_num=str(num_daf), logger=logger)
    return episode


def chassidus_podcast(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.sg_chassidus["dir"], logger=logger)
    local_media.thumbnail = "data/sg-chassidus/sg-chassidus.jpg"
    episode = publish_podcast(local_media, config.sg_chassidus, config, logger=logger)
    print(episode)


def add_youtube_to_chassidus_podcast(file_path_1, url, episode_id):
    file_2: LocalMedia = download_youtube_video(url, config.sg_chassidus["dir"], logger=logger)
    combined = combine_mp3_files(file_path_1, file_2.file_name)
    # combined = combine_mp3_files(file_path_1, file_path_2)
    show_id = config.sg_chassidus["show_id"]
    media_id = upload_media(config=config, show_id=show_id, file_name=combined)
    print(media_id)
    episode = get_episode(config, episode_id)
    episode_url = update_podcast(
        config=config,
        media_id=media_id,
        shows_id=show_id,
        episode_id=episode_id,
        shownotes=episode["shownotes"],
        title=episode["title"],
        date=episode["published_date"],
        status=episode["status"],
        episode_season=episode["episode_season"],
        episode_number=episode["episode_number"],
    )
    print(episode_url)


def chassidus_create_podcast_and_video(file: str, title: str = None, desc: str = "", picture: str = "shloimy.jpg"):
    if title is None:
        title = file.split("/")[-1].split(".")[0]
    local_media = LocalMedia(file_name=file, title=title, description=title + "\n" + desc, thumbnail=picture)

    audio_to_pls(local_media, config.sg_chassidus)
    file = create_video_from_audio_and_picture(file, picture, config.sg_chassidus["dir"] + title + ".mp4")
    local_media.file_name = file
    youtube_url = upload_video_with_options(local_media, privacyStatus="public")
    print(youtube_url)


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
    local_media = LocalMedia(file_name=file, title=title, description=description, thumbnail=picture)
    episode = publish_podcast(local_media, config.halacha, config, logger=logger)

    local_media.file_name = create_video_from_audio_and_picture(file, picture, "data/halacha/" + title + ".mp4")
    print("Uploading to YouTube")
    youtube_url = upload_video_with_options(local_media, privacyStatus="public")

    print(description)


def download2_and_combine(url1: str, url2: str) -> str:
    info1 = download_youtube_video(url1, config.DATA_DIR, logger=logger)
    file1 = info1["file_name"]
    info2 = download_youtube_video(url1, config.DATA_DIR, logger=logger)
    file2 = info2["file_name"]
    combined = combine_mp3_files(file1, file2)
    return combined


def download_combine_and_enhance(url: str, file: str) -> str:
    localMedia: LocalMedia = download_youtube_video(url, "data/", logger=logger)
    combined = combine_mp3_files(file, localMedia["file_name"])
    enhanced_file = enhance_podcast(combined, config, logger=logger)
    return combined


def download_enhance_and_combine(url: str, file: str) -> str:
    localMedia: LocalMedia = download_youtube_video(url, config.DATA_DIR, logger=logger)
    enhanced_file = enhance_podcast(localMedia["file_name"], config, logger=logger)
    combined = combine_mp3_files(file, enhanced_file)
    return combined


def download_and_enhance(url: str) -> str:
    localMedia: LocalMedia = download_youtube_video(url, config.DATA_DIR, logger=logger)
    enhanced_file = enhance_podcast(localMedia["file_name"], config, logger=logger)
    return enhanced_file


def add_youtube_to_pls(file_path_1, url, episode_id):
    local_media: LocalMedia = download_youtube_video(url, config.pls["dir"], logger=logger)
    combined = combine_mp3_files(file_path_1, local_media.file_name)
    show_id = config.pls["show_id"]
    media_id = upload_media(config=config, show_id=show_id, file_name=combined)
    print(media_id)
    episode = get_episode(config, episode_id)
    episode_url = update_podcast(
        config=config,
        media_id=media_id,
        shows_id=show_id,
        episode_id=episode_id,
        shownotes=episode["shownotes"],
        title=episode["title"],
        date=episode["published_date"],
        status=episode["status"],
        episode_season=episode["episode_season"],
        episode_number=episode["episode_number"],
    )

    print(episode_url)


def add_audio_to_pls(file_path_1, file_path_2, episode_id):
    # file_path_2 = enhance_podcast(file_path_2, config)
    combined = combine_mp3_files(file_path_1, file_path_2)
    show_id = config.pls["show_id"]
    media_id = upload_media(config=config, show_id=show_id, file_name=combined)
    print(media_id)
    episode = get_episode(config, episode_id)
    episode_url = update_podcast(
        config=config,
        media_id=media_id,
        shows_id=show_id,
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
    local_media = LocalMedia(file_name=file_path_2, title=title_2, description="trial", thumbnail="shloimy.jpg")

    file = create_video_from_audio_and_picture(file_path_2, "shloimy.jpg", title_2 + ".mp4")
    local_media.file_name = file
    upload_video_with_options(local_media, privacyStatus="public")


def pls_create_video_and_podcast(file: str, title: str = None, desc: str = "", picture: str = "shloimy.jpg"):
    if title is None:
        title = file.split("/")[-1].split(".")[0]
    enhanced_file = enhance_podcast(file, config, logger=logger)

    local_media = LocalMedia(file_name=file, title=title, description=title + "\n" + desc, thumbnail=picture)

    audio_to_pls(local_media, config.pls)
    file = create_video_from_audio_and_picture(file, picture, "data/PLS/" + title + ".mp4")
    local_media.file_name = file
    youtube_url = upload_video_with_options(local_media, privacyStatus="public")
    print(youtube_url)


def youtube_to_pls(url: str):
    localMedia: LocalMedia = download_youtube_video(url, config.pls["dir"], logger=logger)
    audio_to_pls(localMedia, config.pls)


def audio_to_pls(localMedia: LocalMedia, show):
    show_id = show["show_id"]
    media_id = upload_media(config=config, show_id=show_id, file_name=localMedia.file_name)
    episode_url = create_podcast(
        config=config,
        media_id=media_id,
        date=localMedia.upload_date,
        title=localMedia.title,
        shownotes=str(localMedia.description) + "\n" + localMedia.url,
        shows_id=show_id,
        logger=logger,
    )
