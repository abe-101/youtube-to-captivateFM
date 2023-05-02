import feedparser
import requests
from bs4 import BeautifulSoup

from configuration_manager import ConfigurationManager
from spotify import get_latest_spotify_episode_link

# Define the URL of the Apple Podcasts page for your podcast episode
APPLE_URL = "https://podcasts.apple.com/us/podcast/kolel-lhoraah-maasis/id1670169956"
ANHCOR_RRS = "https://anchor.fm/s/955ecec4/podcast/rss"
EPISODE_TITLE = "מסכת סוטה דף ב - Rabbi Shloime Greenwald"


def get_episode_links(episode_title, show, config: ConfigurationManager):
    captivate_link = get_captivate_link(show["rss"], episode_title)
    apple_link = get_apple_link(show["apple_url"], episode_title)
    spotify_link = get_latest_spotify_episode_link(episode_title, show["spotify_id"], config)

    return {"captivate": captivate_link, "apple": apple_link, "spotify": spotify_link}


def get_youtube_id(youtube_channel, episode_title):
    pass


def get_captivate_link(rss, episode_title):
    rss_url = "https://feeds.captivate.fm/" + rss
    feed = feedparser.parse(rss_url)
    for episode in feed.entries:
        if episode["title"] == episode_title:
            return episode["link"]
    return None


def get_apple_link(podcast_url, episode_title):
    """
    Fetches the Apple Podcasts URL for a specific podcast episode based on the episode title.

    Args:
        podcast_url (str): The URL of the Apple Podcasts page for the podcast.
        episode_title (str): The title of the desired podcast episode.

    Returns:
        str: The episode URL that matches the given title, or None if no match found.
    """
    # Send an HTTP GET request to the podcast URL
    response = requests.get(podcast_url)

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the episode link from the HTML structure
    for link in soup.find_all("a"):
        href = link.get("href")
        title = link.text.strip()  # Get the text content of the anchor tag and strip leading/trailing spaces
        if href.startswith("https://podcasts.apple.com/us/podcast/") and title == episode_title:
            return href

    # Return None if no match found
    return None


def get_anchor_link(rss_url, episode_title):
    feed = feedparser.parse(rss_url)
    for episode in feed.entries:
        if episode["title"] == episode_title:
            return episode["links"][0]["href"]
    return None


# Set dynamic variables
daf = "ה"
youtube_link = "https://www.youtube.com/live/WnFK7G3s0Wk"
spotify_link = "https://open.spotify.com/episode/6sVl0hvmnlDuunHBh0cWAa"
apple_podcasts_link = "https://podcasts.apple.com/us/podcast/%D7%9E%D7%A1%D7%9B%D7%AA-%D7%A1%D7%95%D7%98%D7%94-%D7%93%D7%A3-%D7%94-rabbi-shloime-greenwald/id1670169956?i=1000608300118"
google_podcasts_link = "https://podcasts.google.com/feed/aHR0cHM6Ly9hbmNob3IuZm0vcy85NTVlY2VjNC9wb2RjYXN0L3Jzcw/episode/NzljNjI3M2QtZTI2Yi00NmI4LWE1N2QtY2UzZDVhZGQyZDg1?sa=X&ved=0CAUQkfYCahcKEwjg3Ifq_qH-AhUAAAAAHQAAAAAQAQ"


def prepare_collive_embed(links):
    html_template = f"""
<iframe src="{links["anchor"].replace("/episodes/", "/embed/episodes/")}" height="102px" width="400px" frameborder="0" scrolling="no"></iframe>
"""
    return html_template


# Create the HTML template
def prepare_collive_post(links: dict, daf: str, youtube_id: str):
    html_template = f"""
Today’s Shiur in Maseches Sota: Daf {daf}
Are you ready for another exciting shiur in Maseches Sota with Rabbi Shloimy Greenwald? Join us today as we learn daf {daf}. Whether you are a beginner or an expert, you will find something to inspire you and enrich your Torah knowledge. 

<iframe src="{links["anchor"].replace("/episodes/", "/embed/episodes/")}" height="102px" width="400px" frameborder="0" scrolling="no"></iframe>

Today's daf is also available on the following platforms:
<ul>
    <li><a href="https://www.youtube.com/watch?v={youtube_id}">YouTube</a></li>
    <li><a href="{links["spotify"]}">Spotify</a></li>
    <li><a href="{links["apple"]}">Apple Podcasts</a></li>
</ul>

You can also join the shiur live at 8:15 pm at 309 New York Ave (Beis Gimpel Chaim) or online at https://www.youtube.com/@KolelLhoraahMaasis or on COLlive.com. 

Don’t miss this opportunity to learn a whole maseches in 49 days.
To join the WhatsApp group, click here: https://chat.whatsapp.com/CuON9nbQvnWLapQIFXVIE3

<iframe width="560" height="315" src="https://www.youtube.com/embed/{youtube_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
"""
    # <li><a href="{google_podcasts_link}">Google Podcasts</a></li>
    return html_template


def prepare_sharable_post(links: dict, youtube_id: str, video_title: str):
    template = f"""
{video_title}

YouTube - https://www.youtube.com/watch?v={youtube_id}
Spotify - {links["spotify"]}
Apple - {links["apple"]}
"""
    return template
