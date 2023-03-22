from playwright.sync_api import Playwright, sync_playwright, expect

from configuration_manager import ConfigurationManager


def run(playwright: Playwright, info, config: ConfigurationManager) -> None:
    browser = playwright.chromium.launch(headless=config.PLAYWRITE_HEADLESS)
    context = browser.new_context(storage_state="auth.json")

    page = context.new_page()
    page.goto("https://podcasters.spotify.com/pod/dashboard/episode/new")
    print('Uploading audio file')
    file_input = page.locator('input[type=file]')
    file_input.set_input_files(info["file_name"])
    
    print('Waiting for upload to finish')
    page.wait_for_timeout(25000)

    page.get_by_role("button", name="Save episode").click()

    #page.get_by_role("button", name="Browse", exact=True).click()
    #page.get_by_role("button", name="Browse", exact=True).set_input_files("WhatsApp Audio 2023-03-19 at 8.53.09 AM (enhanced).mp3")
    #page.get_by_role("button", name="Save episode").click()
    page.get_by_placeholder("What do you want to call this episode?").click()
    page.get_by_placeholder("What do you want to call this episode?").fill(info["title"])
    page.get_by_role("paragraph").filter(has_text="What else do you want your listeners to know?").click()
    page.get_by_role("textbox").filter(has_text="What else do you want your listeners to know?").fill(info["description"])
    #page.get_by_role("img", name="Episode cover art").click()
    #page.locator("div").filter(has_text="Upload new episode art").nth(1).set_input_files("halacha.jpg")
    #page.get_by_role("button", name="Save").click()

    if config.LOAD_THUMBNAIL:
        print("Uploading thumbnail")
        file_input = page.locator('input[type=file]')
        file_input.set_input_files(info["thumbnail"])
        page.get_by_role("button", name="Save").click()

    if config.SPOTIFY_PODCAST_PUBLISH:
        page.get_by_role("button", name="Publish now").click()
    else:
        page.get_by_role("button", name="Save as draft").click()

    # ---------------------
    context.close()
    browser.close()

def upload_to_spotify_podcasters(info, config):
    with sync_playwright() as playwright:
        run(playwright, info, config)
    return True


