import os


class ConfigurationManager:
    def __init__(self):
        self.USER_ID = os.getenv("USER_ID")
        self.CAPTIVATE_API_KEY = os.getenv("CAPTIVATE_API_KEY")
        self.SHOWS_ID = os.getenv("SHOWS_ID")
        self.DATA_DIR = os.getenv("DATA_DIR")
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.KOLEL_SPOTIFY_ID = os.getenv("KOLEL_SPOTIFY_ID")
        self.PLS_SPOTIFY_ID = os.getenv("PLS_SPOTIFY_ID")
        self.ANCHOR_EMAIL = os.getenv("ANCHOR_EMAIL")
        self.ANCHOR_PASSWORD = os.getenv("ANCHOR_PASSWORD")
