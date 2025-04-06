from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper.utils.web_driver_factory import get_chrome_web_driver, get_firefox_web_driver
from .models import BusinessListing


URL = 'www.bizbuysell.com/'
log = logging.getLogger(__name__)

def scrape(headless, count, skip):
    return scrape_data(headless, count, skip)

    
def scrape_data(headless, count, skip):
    # main_driver = get_firefox_web_driver(headless)
    main_driver = get_chrome_web_driver(headless)

    wait = WebDriverWait(main_driver, 10)

    element_list = []
    try:
        main_driver.get("https://www.bizbuysell.com/buy/")
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.diamond")))
        element_list = main_driver.find_elements(By.CSS_SELECTOR, "a.diamond")
        log.info('Number of Listings found: %s', len(element_list))

        web_listings = extract_listing_details(element_list)

        if skip > len(web_listings):
         skip = 0
        web_listings = web_listings[skip:]
        business_listings = []

        # 🔥 Multithreading
        with ThreadPoolExecutor(max_workers=5) as executor:
            limited_listings = web_listings[:min(count, len(web_listings))]
            futures = [executor.submit(extract_seller_details_threaded, listing, headless) for listing in limited_listings]

            for future in as_completed(futures):
                try:
                  result = future.result()
                  if result and result.description:
                   business_listings.append(result)
                  log.info("Lenght of new list %s", len(business_listings))
                except Exception as e:
                    log.error(f"Error in thread: {e}") 
    finally:
        main_driver.quit()

    
    return business_listings

def extract_seller_details_threaded(listing, headless=True):
    driver = get_chrome_web_driver(headless)
    # driver = get_firefox_web_driver(headless)

    wait = WebDriverWait(driver, 10)

    try:
        return extract_seller_details(listing, driver, wait)
    finally:
        driver.quit()

def extract_seller_details(listing, driver, wait):
    try:
        driver.get(listing.url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Contact button and phone number
        try:
            contact_button = wait.until(EC.element_to_be_clickable((By.ID, listing.contact_button_id)))
            driver.execute_script("arguments[0].click();", contact_button)
            wait.until(EC.staleness_of(contact_button))

            phone_element = wait.until(
                EC.presence_of_element_located((By.ID, f"lblViewTpnTelephone_{listing.listing_id}"))
            )
            listing.seller_contact = phone_element.text
        except TimeoutException as te:
            print(f"[!] Timeout getting contact for {listing.name}: {te}")

        # Seller name
        try:
            seller_name_elem = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "#contactSellerForm > div:nth-child(10) > div:nth-child(1) > div:nth-child(1)"
                
            )))
            log.info('Seller Name without trim %s', seller_name_elem.text)
            listing.seller_name = seller_name_elem.text.replace("Listed By:", "").strip()
        except TimeoutException as te:
            print(f"[!] Timeout getting seller name for {listing.name}: {te}")

        # Title
        heading_element = soup.select_one("h1.bfsTitle")
        listing.name = heading_element.get_text(strip=True) if heading_element else "N/A"

        # Financials
        financials = soup.select(".financials .row p")
        finance_string = ""
        for item in financials:
            title = item.select_one(".title")
            value = item.select_one(".normal")
            if title and value:
                finance_string += f"{title.get_text()} {value.get_text()}\n"
        listing.financials = finance_string

        # Description
        description_elem = soup.select_one(".businessDescription")
        if description_elem:
            listing.description = description_elem.get_text(strip=True)

        # Detailed Info
        details = soup.select(
            "#ctl00_ctl00_Content_ContentPlaceHolder1_wideProfile_listingDetails_dlDetailedInformation dt"
        )
        values = soup.select(
            "#ctl00_ctl00_Content_ContentPlaceHolder1_wideProfile_listingDetails_dlDetailedInformation dd"
        )
        detailed_info = ""
        for d, v in zip(details, values):
            detailed_info += f"{d.get_text()} {v.get_text()}\n"

        listing.blocked = False
        print(f"[✓] Extracted seller info for: {listing.name}")

    except Exception as e:
        print(f"[x] Failed to extract details for {listing.name} — Reason: {str(e)}")
        listing.blocked = True

    return listing


def get_listings(headless):
    driver = get_firefox_web_driver()
    wait = WebDriverWait(driver, 10)
    try:
        driver.get("https://www.bizbuysell.com/buy/")
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.diamond")))
        element_list = driver.find_elements(By.CSS_SELECTOR, "a.diamond")
        log.info('Number of Listings found: %s', len(element_list))
        return extract_listing_details(element_list)
        
    finally:
        driver.quit()

def extract_listing_details(element_list):
    business_listing = []

    try:
        
        for listing in element_list:
            try:
                listing_url = listing.get_attribute("href").rstrip("/")
                listing_id = listing_url.split("/")[-1]
                contact_button_id = f"hlViewTelephone_{listing_id}"
                
                listing_obj = BusinessListing()  # 👈 move inside the loop
                listing_obj.url = listing_url
                listing_obj.listing_id = listing_id
                listing_obj.contact_button_id = contact_button_id
                
                business_listing.append(listing_obj)
            except Exception as e:
                print("Error processing listing:", e)
    except TimeoutException as te:
            print(f"[!] Timeout getting contact for {listing.name}: {te}")            


    return business_listing