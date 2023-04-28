from typing import Dict
from configuration_manager import LocalMedia

from yt_dlp import YoutubeDL


def download_youtube_video(url: str, folder_path: str) -> Dict[str, str]:
    """
    This function downloads a YouTube video from the given URL, and returns a dictionary containing the video's title, description, file name and upload date.

    :param url: The URL of the YouTube video to download
    :type url: str
    :param folder_path: The folder on disk where to download and save the audio
    :type folder_path: str
    :return: A dictionary containing the video's title, description, file name, and upload date
    :rtype: Dict[str, str]
    """
    with YoutubeDL(
        {
            "format": "bestaudio/best",
            "outtmpl": f"{folder_path}/%(title)s.%(ext)s",
            "keepvideo": True,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        }
    ) as ydl:
        video_info = ydl.extract_info(url)

    local_media = LocalMedia(
        file_name=video_info["requested_downloads"][0]["filepath"],
        title=video_info["title"],
        description=video_info.get("description"),
        url=url,
    )
    local_media.set_upload_date_from_string(video_info.get("upload_date"))
    return local_media
    # return {
    #    "title": video_info["title"],
    #    "description": video_info.get("description"),
    #    "file_name": video_info["requested_downloads"][0]["filepath"],
    #    "upload_date": video_info.get("upload_date"),
    #    "url": url,
    # }
