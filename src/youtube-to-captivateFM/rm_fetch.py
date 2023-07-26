import csv
import re

import feedparser
import googleapiclient.errors
import yt_dlp
from configuration_manager import ConfigurationManager
from dotenv import load_dotenv
from generate_post import Video, get_most_recent_videos_from_playlist
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
config = ConfigurationManager()
api_key = config.YOUTUBE_API


def get_new_videos(show):
    playlist_id = show["playlist_id"]

    max_results = 49

    youtube = build("youtube", "v3", developerKey=api_key)
    # Create a YouTube API service object

    db = get_most_recent_videos_from_playlist(youtube, playlist_id, max_results)

    # playlist_url = f"https://www.youtube.com/playlist?list={show['playlist_id']}"
    # ydl_opts = {"dump_single_json": True, "extract_flat": True, "format": "best"}
    #
    # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #    playlist_data = ydl.extract_info(playlist_url, download=False)

    podcast_ids = set()
    podcast_titles = set()

    url = "https://feeds.captivate.fm/" + show["rss"]
    feed = feedparser.parse(url)
    print(len(feed["entries"]))

    for entry in feed["entries"]:
        youutbe_id = find_youtube_video_id(entry["summary"])
        if youutbe_id:
            podcast_ids.add(youutbe_id)
        podcast_titles.add(entry["title"])
    print(f"Podcast ids: {len(podcast_ids)}")
    print(f"Podcast titles: {len(podcast_titles)}")

    youtube = []
    for video in db:
        if video.id not in podcast_ids and video.name not in podcast_titles:
            youtube.append((video.id, video.name))

    print(f"Youtube: {len(youtube)}")
    return youtube


def find_youtube_video_id(text):
    pattern = r"(?:youtube\.com\/watch\?v=|youtu.be\/)([A-Za-z0-9_-]+)"
    match = re.search(pattern, text)
    if match:
        video_id = match.group(1)
        return video_id
    else:
        return None


# create a script that builds a dict where key is video id and value is video title plus description
# then grab all podcast for this show and retreive the youtube id from the description and update the title and description to match YouTube
