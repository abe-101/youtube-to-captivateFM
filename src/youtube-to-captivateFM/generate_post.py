#!/usr/bin/python

import os
import subprocess
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


# from rich import print
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
from collections import namedtuple

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from podcast_links import get_episode_links, prepare_collive_embed, prepare_sharable_post
from configuration_manager import ConfigurationManager

load_dotenv()

config = ConfigurationManager()

YOUTUBE_TO_ANCHORFM = os.getenv("YOUTUBE_TO_ANCHORFM_DIR")
api_key = config.YOUTUBE_API


def get_links(video):
    show_names = [d for d in vars(config) if isinstance(vars(config)[d], dict)]
    print("Choose a Podcast show: ")
    for i, show in enumerate(show_names):
        print(f"{i}: {show}")

    show_num = int(input())
    shows = [vars(config)[d] for d in vars(config) if isinstance(vars(config)[d], dict)]

    links = get_episode_links(video.name, shows[show_num], config)
    # embed = prepare_collive_embed(links)
    post = prepare_sharable_post(links, video.id, video.name)

    # print(embed)
    print(post)


def publish_video(youtube_id: str):
    print(f"Attempting {youtube_id}")
    os.chdir(YOUTUBE_TO_ANCHORFM)
    with open("episode.json", "w") as file:
        file.write(f'{{"id":"{youtube_id}"}}')

    subprocess.run(["npm start"], shell=True)

    print(f"Finished {youtube_id}")


# Specify the channel ID
channel_id = "UCU91spVc-WB73HnPZiEqMNQ"

# Set the number of results to be retrieved (max. 50)
max_results = 15

# Create a YouTube API service object
youtube = build("youtube", "v3", developerKey=api_key)

# Call the YouTube Data API's "search" method to retrieve the most recent
# videos from the specified channel
request = youtube.search().list(
    part="id,snippet",
    channelId=channel_id,
    type="video",
    order="date",
    maxResults=max_results,
    # pageToken="CDIQAA"
)

try:
    # Execute the request
    response = request.execute()


except HttpError as error:
    print(f"An HTTP error occurred: {error}")

Video = namedtuple("Video", ["id", "name", "date"])
db = list()
for video in response["items"]:
    publish_time = video["snippet"]["publishedAt"]
    # convert date to datetime object
    publish_time_dt = datetime.strptime(publish_time, "%Y-%m-%dT%H:%M:%SZ")
    # convert from utc to est
    est_time = publish_time_dt.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("America/New_York"))
    db.append(Video(id=video["id"]["videoId"], name=video["snippet"]["title"], date=est_time))
table = Table(title="Please choose from the following videos:")
table.add_column("#", style="cyan", no_wrap=True)
table.add_column("video ID", style="magenta")
table.add_column("Date and Time", style="green")
table.add_column("Name", style="cyan", no_wrap=True)

for i, v in enumerate(db):
    table.add_row(str(i + 1), v.id, str(v.date), v.name)
    # print(i + 1, " | ", v.id, " | ", v.date, " | ", v.name)

console = Console()
console.print(table)


choices = Prompt.ask(
    "Enter your choices separated by a comma: ", default="0", choices=[str(i) for i in range(len(db) + 1)]
)

choices = choices.split(",")

for choice in choices:
    if choice == "0":
        ids = input("Enter your video id's separated by a comma: ")
        ids = ids.split(",")
        for id in ids:
            publish_video(id)
    else:
        get_links(db[int(choice) - 1])
