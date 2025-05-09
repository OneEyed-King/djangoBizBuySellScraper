from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import FirefoxOptions
import asyncio
from camoufox.async_api import AsyncCamoufox 
import random
from decouple import config
import logging


log = logging.getLogger(__name__)
PROXIES = config("PROXIES").split(",")

def get_chrome_web_driver(headless, use_proxy):
    options = Options()

    # Run in headless mode if specified
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-http2")
    options.add_argument("--disable-infobars")

    # Select a random proxy from the list
    random_proxy = random.choice(PROXIES).split(':')
    log.info(f"Random proxy picked: {random_proxy}")

    if random_proxy and len(random_proxy) == 4:
        server = f"{random_proxy[0]}:{random_proxy[1]}"
        username = random_proxy[2]
        password = random_proxy[3]
        implemented_proxy = {
            "server": server,
            "username": username,
            "password": password
        }
        
        # Configure the proxy
        options.add_argument(f"--proxy-server={server}")
        options.add_argument(f"--proxy-auth={username}:{password}")
    else:
        implemented_proxy = None

    log.info(f"Implemented Proxy: {implemented_proxy}")

    # Initialize Chrome WebDriver
    service = Service("chromedriver")  # Ensure ChromeDriver is in PATH or specify the full path
    driver = webdriver.Chrome(service=service, options=options)

    return driver


# def get_chrome_web_driver(headless):
#     options = Options()
#     if headless:
#      options.add_argument("--headless")  # run in background
#     options.add_argument("--disable-gpu")

#     driver = webdriver.Chrome(options=options)
#     # wait = WebDriverWait(driver, 10)
#     return driver

def get_firefox_web_driver(headless):
    options = FirefoxOptions()
    if headless:
     options.add_argument("--headless")  # Optional
    # options.set_preference("dom.webdriver.enabled", False)
    # options.set_preference("useAutomationExtension", False)

    # service = Service(executable_path=GeckoDriverManager().install())
    driver =webdriver.Firefox(options=options)
    return driver

async def get_camoufox_browser(headless, proxy=None):
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
    ).__aenter__()


