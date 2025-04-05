from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import FirefoxOptions

def get_chrome_web_driver(headless):
    options = Options()
    if headless:
     options.add_argument("--headless")  # run in background
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    # wait = WebDriverWait(driver, 10)
    return driver

def get_firefox_web_driver(headless):
    options = FirefoxOptions()
    if headless:
     options.add_argument("--headless")  # Optional
    # options.set_preference("dom.webdriver.enabled", False)
    # options.set_preference("useAutomationExtension", False)

    # service = Service(executable_path=GeckoDriverManager().install())
    driver =webdriver.Firefox(options=options)
    return driver


