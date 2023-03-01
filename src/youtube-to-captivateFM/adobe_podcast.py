import os
from playwright.sync_api import Playwright, sync_playwright

from audio_conversion import convert_wav_to_mp3


# Function to run the audio enhancement process using Adobe Podcast
def run(playwright: Playwright, file_name: str) -> None:
    new_file = file_name.rsplit(".", 1)[0] + " (enhanced).mp3"
    # check if file was already enhanced
    if os.path.exists(new_file):
        print(f"file: {file_name} was already enhanced, skipping")
        return new_file
    # Launch the chromium browser
    browser = playwright.chromium.launch(headless=False)

    # Create a new context with saved authentication information
    # For first-time users, sign in manually and save the session and cookies using the command:
    # playwright codegen --save-storage=auth.json https://podcast.adobe.com/enhance#
    # More details:
    # https://playwright.dev/python/docs/cli#preserve-authenticated-state
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()
    # Go to the Adobe Podcast enhance page
    page.goto("https://podcast.adobe.com/enhance#")
    # Upload the audio file
    page.get_by_label("Upload").set_input_files(file_name)
    # Wait for the "Download" button to become available
    page.get_by_role("button", name="Download").wait_for(timeout=800000)

    print("Downloading the enhanced file")
    # Triggers the download of the enhanced file and gets its info
    with page.expect_download() as download_info:
        # Perform the action that initiates download
        page.get_by_role("button", name="Download").click()
    download = download_info.value
    # Waits for the download process to complete
    print(download.path())
    # Converts the enhanced audio from WAV to MP3 using FFmpeg
    print("doint the ffmpeg thing")
    new_name = convert_wav_to_mp3(download.path(), new_file)

    # ---------------------
    # Closes the context and browser instance
    context.close()
    browser.close()

    return new_name


def enhance_podcast(file_name: str) -> str:
    with sync_playwright() as playwright:
        new_file = run(playwright, file_name)
    return new_file


if __name__ == "__main__":
    # Prompts the user for the audio file to enhance
    file_name = input("Which file would you like to enhance? ")
    new_file = enhance_podcast(file_name)
    print(new_file)
