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
from podcast_links import get_episode_links, prepare_collive_embed, prepare_collive_post, prepare_sharable_post
from spotify import get_latest_spotify_episode_link
from upload_video import upload_video_with_options

load_dotenv()

config = ConfigurationManager()


def all_kolel():
    with open("needs_podcasts.csv") as f:
        for line in f:
            kolel(line[:11])


def kolel(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.kolel["dir"])
    print(local_media)
    episode = publish_podcast(local_media, config.kolel, config)
    return episode


def meseches_sota_shiur(youtube_url: str, num_daf: int):
    local_media: LocalMedia = download_youtube_video(youtube_url, config.sota["dir"])

    print("getting thumbnail")
    client = ImgurClient(config.IMGUR_CLIENT_ID, config.IMGUR_CLIENT_SECRET)
    pic = config.sota["dir"] + "square-lower/0" + str(num_daf) + ".jpg"
    print(pic)
    uploaded_image = client.upload_from_path(pic)
    print(uploaded_image["link"])
    local_media.thumbnail = uploaded_image["link"]
    episode = publish_podcast(local_media, config.sota, config, episode_num=str(num_daf))
    return episode


def chassidus_podcast(url: str):
    local_media: LocalMedia = download_youtube_video(url, config.sg_chassidus["dir"])
    # local_media.thumbnail = "data/sg-chassidus/sg-chassidus.jpg"
    episode = publish_podcast(local_media, config.sg_chassidus, config)
    print(episode)


def add_youtube_to_chassidus_podcast(file_path_1, url, episode_id):
    file_2: LocalMedia = download_youtube_video(url, config.sg_chassidus["dir"])
    combined = combine_mp3_files(file_path_1, file_2.file_name)
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
    episode = publish_podcast(local_media, config.halacha, config)

    local_media.file_name = create_video_from_audio_and_picture(file, picture, "data/halacha/" + title + ".mp4")
    print("Uploading to YouTube")
    youtube_url = upload_video_with_options(local_media, privacyStatus="public")

    print(description)


def download2_and_combine(url1: str, url2: str) -> str:
    info1 = download_youtube_video(url1, config.DATA_DIR)
    file1 = info1["file_name"]
    info2 = download_youtube_video(url1, config.DATA_DIR)
    file2 = info2["file_name"]
    combined = combine_mp3_files(file1, file2)
    return combined


def download_combine_and_enhance(url: str, file: str) -> str:
    localMedia: LocalMedia = download_youtube_video(url, "data/")
    combined = combine_mp3_files(file, localMedia["file_name"])
    enhanced_file = enhance_podcast(combined, config)
    return combined


def download_enhance_and_combine(url: str, file: str) -> str:
    localMedia: LocalMedia = download_youtube_video(url, config.DATA_DIR)
    enhanced_file = enhance_podcast(localMedia["file_name"], config)
    combined = combine_mp3_files(file, enhanced_file)
    return combined


def download_and_enhance(url: str) -> str:
    localMedia: LocalMedia = download_youtube_video(url, config.DATA_DIR)
    enhanced_file = enhance_podcast(localMedia["file_name"], config)
    return enhanced_file


def add_youtube_to_pls(file_path_1, url, episode_id):
    local_media: LocalMedia = download_youtube_video(url, config.pls["dir"])
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
    local_media = LocalMedia(
        file_name=file_path_2, title=title_2, description=episode["shownotes"], thumbnail="shloimy.jpg"
    )

    file = create_video_from_audio_and_picture(file_path_2, "shloimy.jpg", title_2 + ".mp4")
    upload_video_with_options(local_media, privacyStatus="public")


def pls_create_video_and_podcast(file: str, title: str, desc: str = "", picture: str = "shloimy.jpg"):
    # enhanced_file = enhance_podcast(file, config)

    local_media = LocalMedia(file_name=file, title=title, description=title + "\n" + desc, thumbnail=picture)

    audio_to_pls(local_media, config.pls)
    file = create_video_from_audio_and_picture(file, picture, "data/PLS" + title + ".mp4")
    youtube_url = upload_video_with_options(local_media, privacyStatus="public")
    print(youtube_url)


def youtube_to_pls(url: str):
    localMedia: LocalMedia = download_youtube_video(url, config.pls["dir"])
    audio_to_pls(localMedia)


def audio_to_pls(localMedia: LocalMedia, show):
    show_id = show["show_id"]
    media_id = upload_media(config=config, show_id=show_id, file_name=localMedia["file_name"])
    episode_url = create_podcast(
        config=config,
        media_id=media_id,
        date=formatted_upload_date,
        title=localMedia["title"],
        shownotes=localMedia["description"] + "\n" + localMedia["url"],
        shows_id=show_id,
    )
