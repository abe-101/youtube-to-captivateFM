#!/usr/bin/python

import os
from collections import namedtuple
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.console import Console

# from rich import print
from rich.prompt import Prompt
from rich.table import Table

from configuration_manager import ConfigurationManager
from podcast_links import get_episode_links, Links, prepare_sharable_post
from tiny_url import TinyURLAPI

load_dotenv()

config = ConfigurationManager()

YOUTUBE_TO_ANCHORFM = os.getenv("YOUTUBE_TO_ANCHORFM_DIR")
api_key = config.YOUTUBE_API

class Video:
    def __init__(self, id, name, date):
        self.id = id
        self.name = name
        self.date = date
        self.links: Links = None

    def get_tiny_urls(self, create: TinyURLAPI, short_name: str):
        self.links["youtube"] = create.get_or_create_alias_url(f"https://youtu.be/{self.id}", f"YouTube-{short_name}")
        self.links["spotify"] = create.get_or_create_alias_url(self.links["spotify"], f"Spotify-{short_name}")
        self.links["apple"] = create.get_or_create_alias_url(self.links["apple"], f"Apple-{short_name}")
        return f"{self.links['youtube'][8:]}\n{self.links['spotify'][8:]}\n{self.links['apple'][8:]}"

        


def get_links(video: Video):
    show_names = [d for d in vars(config) if isinstance(vars(config)[d], dict)]
    print("Choose a Podcast show: ")
    for i, show in enumerate(show_names):
        print(f"{i}: {show}")

    show_num = int(input())
    shows = [vars(config)[d] for d in vars(config) if isinstance(vars(config)[d], dict)]

    video.links = get_episode_links(video.name, shows[show_num], config)
    post = prepare_sharable_post(video.links, video.id, video.name)
    if any(value is None for value in video.links.values()):
        user_input = input("At least one value is None. Do you want to continue? (yes/no): ")
        if user_input.lower() != "yes":
            print(post)
            exit()

    creator = TinyURLAPI(config.TINY_URL_API_KEY)
    match show_names[show_num]:
        case "pls":
            l = video.get_tiny_urls(creator, "pls1234")
            print(video.name)
            print(l)

            pass
        case "gittin":
            digits = "".join([char for char in video.name if char.isdigit()])
            l = video.get_tiny_urls(creator, f"Gittin-{digits}")
            print(video.name + "\n")
            print(l)
            print("\n")
            print("Short on time? Listen to a recap: ")
        case "halacha":
            today = datetime.today()
            formatted_date = today.strftime("%m-%d")

            l = video.get_tiny_urls(creator, "halacha-" + formatted_date)
            print(video.name + "\n")
            print(l)
        case "kolel":
            print(post)
        case "sg_chassidus":
            print(post)



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
)

try:
    # Execute the request
    response = request.execute()


except HttpError as error:
    print(f"An HTTP error occurred: {error}")

#Video = namedtuple("Video", ["id", "name", "date"])
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
    get_links(db[int(choice) - 1])
