#!/usr/bin/python

import asyncio
import logging
import re
import time
from datetime import datetime

from adobe_podcast import enhance_podcast
from audio_conversion import (combine_mp3_files, combine_webm_files,
                              convert_wav_to_mp3,
                              create_video_from_audio_and_picture)
from captivate_api import (create_podcast, format_date, get_episode,
                           publish_podcast, update_podcast, upload_media)
from configuration_manager import ConfigurationManager, LocalMedia
from dotenv import load_dotenv
from download_yt import download_youtube_video
from imgurpython import ImgurClient
from rm_fetch import get_new_videos
from spotify import get_latest_spotify_episode_link
from upload_video import upload_video_with_options

# Set up logging configuration
logging.basicConfig(
    filename="ry-minkowicz.log", level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get a logger instance for the current module
logger = logging.getLogger(__name__)


load_dotenv()

config = ConfigurationManager()


def happy_playlist():
    new_videos = get_new_videos(config.rm_happy)
    n = len(new_videos)
    count = 1
    for id, title in new_videos:
        print(f"Downloading({count}/{n}) - {title}")
        happy_podcast(id)
        count += 1


def tanya_playlist():
    new_videos = get_new_videos(config.rm_tanya)
    for id, title in new_videos:
        print(f"Downloading {title}")
        tanya_podcast(id)


def maamor_playlist():
    new_videos = get_new_videos(config.rm_maamor)
    n = len(new_videos)
    count = 1
    for id, title in new_videos:
        print(f"Downloading({count}/{n}) - {title}")
        maamor_podcast(id)
        count += 1


def torah_playlist():
    new_videos = get_new_videos(config.rm_torah)
    n = len(new_videos)
    count = 1
    for id, title in new_videos:
        print(f"Downloading({count}/{n}) - {title}")
        torah_podcast(id)
        count += 1


def maamor_podcast(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.rm_maamor["dir"], logger=logger)
    episode = publish_podcast(local_media, config.rm_maamor, config)
    print(episode)


def happy_podcast(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.rm_happy["dir"], logger=logger)
    string = local_media.title
    match = re.search(r"Day\s+(\d+)", string)

    if match:
        number = match.group(1)
        print(number)
    else:
        number = 1
    episode = publish_podcast(local_media, config.rm_happy, config, episode_num=number, logger=logger)
    print(episode)


def tanya_podcast(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.rm_tanya["dir"], logger=logger)

    string = local_media.title

    # Use regular expression to find the number
    match = re.search(r"\d+", string)

    if match:
        number = match.group()
        print(number)
    else:
        number = 1

    episode = publish_podcast(local_media, config.rm_tanya, config, episode_num=number, logger=logger)
    print(episode)


def torah_podcast(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.rm_torah["dir"], logger=logger)
    episode = publish_podcast(local_media, config.rm_torah, config, logger=logger)
    print(episode)


def shuchat_podcast(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.shuchat["dir"], logger=logger)
    episode = publish_podcast(local_media, config.shuchat, config, logger=logger)
    print(episode)


def shuchat_playlist():
    new_videos = get_new_videos(config.shuchat)
    n = len(new_videos)
    count = 1
    for id, title in new_videos:
        print(f"Downloading({count}/{n}) - {title}")
        shuchat_podcast(id)
        count += 1
