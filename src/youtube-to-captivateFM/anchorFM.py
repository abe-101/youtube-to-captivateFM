import asyncio
from pyppeteer import launch

# from dotenv import load_dotenv
#
# load_dotenv()
#
#
# class Env:
#    default_values = {
#        "EPISODE_PATH": ".",
#        "ANCHOR_EMAIL": "",
#        "ANCHOR_PASSWORD": "",
#        "UPLOAD_TIMEOUT": 60 * 5 * 1000,
#        "SAVE_AS_DRAFT": False,
#        "LOAD_THUMBNAIL": False,
#        "IS_EXPLICIT": False,
#        "URL_IN_DESCRIPTION": False,
#        "POSTPROCESSOR_ARGS": "",
#        "SET_PUBLISH_DATE": False,
#        # "AUDIO_FILE_FORMAT": "mp3",
#        # "AUDIO_FILE_TEMPLATE": "episode.%(ext)s",
#        # "THUMBNAIL_FILE_FORMAT": "jpg",
#        # "THUMBNAIL_FILE_TEMPLATE": "thumbnail.%(ext)s",
#        "PUPETEER_HEADLESS": True,
#    }
#
#    def __getattr__(self, name):
#        value = os.environ.get(name, self.default_values.get(name))
#        if value is None:
#            raise AttributeError(f"Undefined environment variable {name}")
#        return value
#
#    def __setattr__(self, name, value):
#        raise NotImplementedError("Cannot modify environment variables")
#
#
# env = Env()


def addUrlToDescription(youtube_video_info, URL_IN_DESCRIPTION: bool):
    if URL_IN_DESCRIPTION:
        return f"{youtube_video_info['description']}\n{youtube_video_info['url']}"
    else:
        return youtube_video_info["description"]


async def setPublishDate(page, navigationPromise, date):
    print("-- Setting publish date")
    publishDateButtonSelector = '//span[contains(text(),"Publish date:")]/following-sibling::button'
    publishDateButton = await page.xpath(publishDateButtonSelector)
    await publishDateButton[0].click()
    await navigationPromise

    await resetDatePickerToSelectYears(page, navigationPromise)
    await selectYearInDatePicker(page, navigationPromise, date.year)
    await selectMonthInDatePicker(page, navigationPromise, date.month)
    await selectDayInDatePicker(page, navigationPromise, date.day)

    confirmButtonSelector = '//span[contains(text(),"Confirm")]/parent::button'
    confirmButton = await page.xpath(confirmButtonSelector)
    await confirmButton[0].click()
    await navigationPromise


async def resetDatePickerToSelectYears(page, navigationPromise):
    for i in range(2):
        datePickerSwitchButtonSelector = 'th[class="rdtSwitch"]'
        datePickerSwitchButton = await page.querySelector(datePickerSwitchButtonSelector)
        await datePickerSwitchButton.click()
        await navigationPromise


async def selectYearInDatePicker(page, navigationPromise, year):
    rdtPrev = await page.querySelector('th[class="rdtPrev"]')
    currentLowestYear = await page.evaluate(
        'e => e.getAttribute("data-value")', await page.querySelector("tbody > tr:first-child > td:first-child")
    )
    while int(currentLowestYear) > int(year):
        await rdtPrev.click()
        await navigationPromise

        currentLowestYear = await page.evaluate(
            'e => e.getAttribute("data-value")', await page.querySelector("tbody > tr:first-child > td:first-child")
        )

    rdtNext = await page.querySelector('th[class="rdtNext"]')
    currentHighestYear = await page.evaluate(
        'e => e.getAttribute("data-value")', await page.querySelector("tbody > tr:last-child > td:last-child")
    )
    while int(currentHighestYear) < int(year):
        await rdtNext.click()
        await navigationPromise

        currentHighestYear = await page.evaluate(
            'e => e.getAttribute("data-value")', await page.querySelector("tbody > tr:last-child > td:last-child")
        )

    tdYear = await page.querySelector(f'tbody > tr > td[data-value="{year}"]')
    await tdYear.click()
    await navigationPromise


async def selectMonthInDatePicker(page, navigationPromise, month):
    tdMonth = await page.xpath(f'//tbody/tr/td[contains(text(),"{month}")]')
    await tdMonth[0].click()
    await navigationPromise


async def selectDayInDatePicker(page, navigationPromise, day):
    dayWithRemovedZeroPad = int(day)
    tdDay = await page.querySelector(
        f'tbody > tr > td[data-value="{dayWithRemovedZeroPad}"][class*="rdtDay"]:not([class*="rdtOld"]:not([class*="rtdNew"])'
    )
    await tdDay.click()
    await navigationPromise


# async def post_episode_anchorfm(youtubeVideoInfo, url_description: bool = True,):
async def post_episode_anchorfm(
    youtubeVideoInfo,
    ANCHOR_EMAIL: str = None,
    ANCHOR_PASSWORD: str = None,
    PUPETEER_HEADLESS: bool = True,
    URL_IN_DESCRIPTION: bool = True,
    SET_PUBLISH_DATE: bool = False,
    IS_EXPLICIT: bool = False,
    LOAD_THUMBNAIL: str = None,
    SAVE_AS_DRAFT: bool = True,
    UPLOAD_TIMEOUT: int = 60 * 5 * 1000,
):
    if ANCHOR_EMAIL is None or ANCHOR_PASSWORD is None:
        print("please provide username and password for anchorFM")
        return

    print("Launching Pyppeteer")
    browser = await launch(args=["--no-sandbox"], headless=PUPETEER_HEADLESS)
    page = await browser.newPage()

    navigationPromise = await page.waitForNavigation()
    await page.goto("https://anchor.fm/dashboard/episode/new")
    await page.setViewport({"width": 1600, "height": 789})

    print("Trying to log in")
    await page.type("#email", ANCHOR_EMAIL)
    await page.type("#password", ANCHOR_PASSWORD)
    await page.click("button[type=submit]")
    await page.waitForNavigation()
    print("Logged in")

    print("Uploading audio file")
    await page.waitForSelector("input[type=file]")
    inputFile = await page.querySelector("input[type=file]")
    await inputFile.uploadFile(youtubeVideoInfo["file_name"])

    print("Waiting for upload to finish")
    await asyncio.sleep(25)

    saveEpisodeButtonSelector = '//span[contains(text(),"Save")]/parent::button[not(boolean(@disabled))]'
    await page.waitForXPath(saveEpisodeButtonSelector, {"timeout": UPLOAD_TIMEOUT})
    saveButton = await page.xpath(saveEpisodeButtonSelector)
    await saveButton[0].click()
    await page.waitForNavigation()

    print("-- Adding title")
    await page.waitForSelector("#title", {"visible": True})
    # Wait some time so any field refresh doesn't mess up with our input
    await asyncio.sleep(2)
    await page.type("#title", youtubeVideoInfo["title"])

    print("-- Adding description")
    await page.waitForSelector('div[role="textbox"]', {"visible": True})
    finalDescription = addUrlToDescription(youtubeVideoInfo, URL_IN_DESCRIPTION)
    await page.type('div[role="textbox"]', finalDescription)

    if SET_PUBLISH_DATE:
        await setPublishDate(page, navigationPromise, youtubeVideoInfo["uploadDate"])

    print("-- Selecting content type")
    selectorForExplicitContentLabel = (
        'label[for="podcastEpisodeIsExplicit-true"]' if IS_EXPLICIT else 'label[for="podcastEpisodeIsExplicit-false"]'
    )
    await page.waitForSelector(selectorForExplicitContentLabel, {"visible": True})
    contentTypeLabel = await page.querySelector(selectorForExplicitContentLabel)
    await contentTypeLabel.click()

    if LOAD_THUMBNAIL:
        print("-- Uploading episode art")
        await page.waitForSelector('input[type=file][accept="image/*"]')
        inputEpisodeArt = await page.querySelector('input[type=file][accept="image/*"]')
        await inputEpisodeArt.uploadFile(LOAD_THUMBNAIL)

        print("-- Saving uploaded episode art")
        saveThumbnailButtonSelector = '//span[text()="Save"]/parent::button'
        await page.waitForXPath(saveThumbnailButtonSelector)
        saveEpisodeArtButton = await page.xpath(saveThumbnailButtonSelector)
        await saveEpisodeArtButton[0].click()
        await page.waitForXPath('//div[@aria-label="image uploader"]', {"hidden": True, "timeout": UPLOAD_TIMEOUT})

    saveDraftOrPublishOrScheduleButtonDescription = getSaveDraftOrPublishOrScheduleButtonDescription(
        SAVE_AS_DRAFT, SET_PUBLISH_DATE
    )
    print(f"-- {saveDraftOrPublishOrScheduleButtonDescription['message']}")

    saveDraftOrPublishOrScheduleButton = await page.xpath(saveDraftOrPublishOrScheduleButtonDescription["xpath"])
    await saveDraftOrPublishOrScheduleButton[0].click()
    await page.waitForNavigation()

    print("Yay")


def getSaveDraftOrPublishOrScheduleButtonDescription(SAVE_AS_DRAFT, SET_PUBLISH_DATE):
    if SAVE_AS_DRAFT:
        return {"xpath": '//button[text()="Save as draft"]', "message": "Saving draft"}
    elif SET_PUBLISH_DATE:
        return {"xpath": '//span[text()="Schedule episode"]/parent::button', "message": "Scheduling"}
    else:
        return {"xpath": '//span[text()="Publish now"]/parent::button', "message": "Publishing"}