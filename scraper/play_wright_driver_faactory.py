import asyncio
from camoufox.async_api import AsyncCamoufox 
import random
from playwright.async_api import async_playwright
from playwright.async_api import Playwright
from decouple import config

PROXIES = config("PROXIES").split(",")

# List of available browser launcher functions
AVAILABLE_BROWSERS = [
    "chrome",
    "firefox",
    "camoufox"
]

async def get_play_random_browser(headless, proxy):
    """
    Randomly selects a browser type and returns the launched browser instance.
    """
    browser_type = random.choice(AVAILABLE_BROWSERS)

    if browser_type == "chrome":
        return await get_play_chrome_browser(headless, proxy)
    elif browser_type == "firefox":
        return await get_play_firefox_browser(headless, proxy)
    elif browser_type == "camoufox":
        return await get_play_camoufox_browser(headless, proxy)
    else:
        raise ValueError("Unsupported browser type selected.")


async def get_play_camoufox_browser(headless, proxy):
    """
    Initializes AsyncCamoufox browser with optional proxy.
    """
    random_proxy = random.choice(PROXIES).split(':')

    return await AsyncCamoufox(
        headless=headless,
        proxy={
            'server': random_proxy[0]+':'+random_proxy[1],
            'username': random_proxy[2],
            'password': random_proxy[3]
        },
        geoip=True
        # stealth=True,           # enables stealth mode
        # block_resources=True,   # blocks images, ads, etc.
        # locale='en-US',         # helps mimic real user
        # timezone='America/New_York',  # sets consistent timezone
    ).__aenter__()



async def get_play_chrome_browser(headless, proxy):
    random_proxy = random.choice(PROXIES).split(':')
    print(random_proxy)
    playwright = await async_playwright().start()
    if random_proxy[0] and proxy:
        implemented_proxy = {
            "server":   random_proxy[0]+':'+random_proxy[1],
            "username": random_proxy[2],
            "password": random_proxy[3],
        }
    else:
        implemented_proxy = None

    print(implemented_proxy)    
    browser = await playwright.chromium.launch(
        headless=headless,
        args=[
            "--disable-http2",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-default-apps",
            "--disable-gpu",
            "--disable-infobars",
        ],
        proxy=implemented_proxy,
    )

    # Attach playwright to browser for later cleanup if needed
    browser._my_playwright = playwright
    return browser



async def get_play_firefox_browser(headless, proxy):
    random_proxy = random.choice(PROXIES).split(':')

    playwright = await async_playwright().start()

    browser = await playwright.firefox.launch(
        headless=headless,
        # args=[
        #     "--disable-blink-features=AutomationControlled"
        # ],
        proxy={
            "server":   random_proxy[0]+':'+random_proxy[1],
            "username": random_proxy[2],
            "password": random_proxy[3],
        },
    )

    # Attach playwright to browser for later cleanup if needed
    browser._my_playwright = playwright
    return browser