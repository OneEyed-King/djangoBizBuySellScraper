import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright 
import logging
from scraper.play_wright_driver_faactory import get_play_chrome_browser, get_play_firefox_browser, get_play_random_browser
from scraper.utils.web_driver_factory import get_camoufox_browser
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import Playwright as playwright
from playwright_stealth import stealth_async
from asyncio import Semaphore
from .models import BusinessListing
import re

URL = 'https://www.bizbuysell.com/buy/'
# URL = 'https://httpbin.org/ip'
log = logging.getLogger(__name__)
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
PAGE_GOTO_TIMEOUT = 30000  # 30 seconds
MAX_CONCURRENT_PAGES = 3

# Prevent image requests to speed up scraping and reduce data usage
async def block_images(page):
    await page.route("**/*", lambda route, request: route.abort() if request.resource_type == "image" else route.continue_())



async def scrape_with_play_wright(headless, count, skip, use_proxy):
    return await scrape_data(headless, count, skip, use_proxy)

async def scrape_data(headless, count, skip, use_proxy):
    async with async_playwright() as p:
        browser = await get_play_chrome_browser(headless, use_proxy)
        page = await browser.new_page()
        await block_images(page)
        await stealth_async(page)

        for attempt in range(MAX_RETRIES):
            try:
                await page.goto(URL, timeout=PAGE_GOTO_TIMEOUT, wait_until="load")
                await page.wait_for_selector("a.diamond", timeout=10000, state="attached")
                break
            except PlaywrightTimeoutError:
                log.warning(f"[Attempt {attempt + 1}] Timeout loading URL: {URL}")
                if attempt == MAX_RETRIES - 1:
                    await browser.close()
                    return []
                await asyncio.sleep(RETRY_DELAY)

        elements = await page.query_selector_all("a.diamond")
        web_listings = await extract_listing_details(elements)

        if skip > len(web_listings):
            skip = 0
        web_listings = web_listings[skip:]

        # Fetch existing from DB and decide what's left to scrape
        existing_records, to_scrape_all = get_existing_and_new_listings(web_listings, count)
        log.info(f"✅ Existing records found: {len(existing_records)}")

        business_listings = existing_records[:count]  # Only take as many existing as needed

        remaining = count - len(business_listings)
        if remaining <= 0:
            await browser.close()
            return business_listings

        to_scrape = to_scrape_all  # don't limit here
        current_index = 0

        while len(business_listings) < count and current_index < len(to_scrape):
            batch = to_scrape[current_index:current_index + 3]
            if not batch:
                break

            results = await extract_seller_details_batch(batch, headless, use_proxy, batch_size=3)

            for result in results:
                if result and result.description and not result.blocked:
                    business_listings.append(result)
                    if len(business_listings) == count:
                        break

            current_index += 3

        await browser.close()
        save_listing_to_mongo(business_listings)
        return business_listings[:count]


# async def scrape_data(headless, count, skip, use_proxy):
#     # from .mongo_client import get_mongo_collection

#     async with async_playwright() as p:
#         browser = await get_play_chrome_browser(headless, use_proxy)
#         page = await browser.new_page()
#         await block_images(page)
#         await stealth_async(page)

#         for attempt in range(MAX_RETRIES):
#             try:
#                 await page.goto(URL, timeout=PAGE_GOTO_TIMEOUT, wait_until="load")
#                 await page.wait_for_selector("a.diamond", timeout=10000, state="attached")
#                 break
#             except PlaywrightTimeoutError:
#                 log.warning(f"[Attempt {attempt + 1}] Timeout loading URL: {URL}")
#                 if attempt == MAX_RETRIES - 1:
#                     await browser.close()
#                     return []
#                 await asyncio.sleep(RETRY_DELAY)

#         elements = await page.query_selector_all("a.diamond")
#         web_listings = await extract_listing_details(elements)

#         if skip > len(web_listings):
#             skip = 0
#         web_listings = web_listings[skip:]

#         existing_records, to_scrape = get_existing_and_new_listings(web_listings, count)
#         log.info(f'existing listings: {existing_records}')

#         business_listings = existing_records.copy()
#         current_index = 0
#         # remaining = count - len(business_listings)
#         # dynamic_batch_size = min(5, remaining, len(batch)) 
#         # dynamic_batch_size = min(5, count)

#         while len(business_listings) < count and current_index < len(to_scrape):
#             remaining = count - len(business_listings)
#             # batch_size = min(dynamic_batch_size, remaining)
#             # batch = to_scrape[current_index:current_index + batch_size]
#             batch = to_scrape[current_index:current_index + min(3, remaining)]
#             batch_size = len(batch)

#             results = await extract_seller_details_batch(batch, headless, use_proxy, batch_size=batch_size)

#             valid_results = []
#             for result in results:
#                 if result and result.description and not result.blocked:
#                     valid_results.append(result)
#                     business_listings.append(result)
#                     if len(business_listings) == count:
#                         break

#             dynamic_batch_size = min(15, count - len(business_listings), len(batch) - len(valid_results))
#             dynamic_batch_size = max(dynamic_batch_size, 1)

#             current_index += len(batch)

#         await browser.close()
#         save_listing_to_mongo(business_listings)
#         return business_listings

def get_existing_and_new_listings(web_listings, count):
    from .mongo_client import get_mongo_collection
    collection = get_mongo_collection("business_listings")

    all_urls = [l.url for l in web_listings]
    existing_docs = list(collection.find({"url": {"$in": all_urls}}))
    existing_urls = {doc["url"] for doc in existing_docs}

    existing_records = []
    to_scrape = []
    for listing in web_listings:
        if listing.url in existing_urls:
            existing_doc = next((doc for doc in existing_docs if doc["url"] == listing.url), None)
            if existing_doc:
                existing_records.append(existing_doc)
        else:
            to_scrape.append(listing)

    return existing_records, to_scrape




# def get_existing_and_new_listings(web_listings, count):
#     from .mongo_client import get_mongo_collection
#     collection = get_mongo_collection("business_listings")

#     urls_to_check = [l.url for l in web_listings[:count]]
#     existing = list(collection.find({"url": {"$in": urls_to_check}}))
#     existing_urls = {doc["url"] for doc in existing}

#     existing_records = existing

#     to_scrape = [l for l in web_listings if l.url not in existing_urls][:count - len(existing_records)]
#     return existing_records, to_scrape


async def extract_seller_details_batch(listings, headless, use_proxy, batch_size=15):
    semaphore = Semaphore(batch_size)
    results = []

    async def process_listing(listing):
        for attempt in range(MAX_RETRIES):
            browser = None
            try:
                browser = await get_play_chrome_browser(headless, use_proxy)
                page = await browser.new_page()
                await block_images(page)
                await stealth_async(page)

                log.info(f"🔄 Attempt {attempt+1} for {listing.url}")
                result = await extract_seller_details(page, listing)

                await page.close()
                await browser.close()

                if not result.blocked:
                    return result

            except Exception as e:
                log.warning(f"[!] Error on attempt {attempt+1} for {listing.url}: {e}")
            finally:
                try:
                    if browser:
                        await browser.close()
                except:
                    pass
            await asyncio.sleep(RETRY_DELAY)

        listing.blocked = True
        log.error(f"[x] Blocked after {MAX_RETRIES} retries: {listing.url}")
        return listing

    tasks = []
    for listing in listings:
        async def task_fn(listing=listing):
            async with semaphore:
                return await process_listing(listing)

        tasks.append(task_fn())

    results = await asyncio.gather(*tasks)
    return [res for res in results if res and not res.blocked]


def save_listing_to_mongo(listing_data):
    from .mongo_client import get_mongo_collection
    from pymongo.errors import DuplicateKeyError
    collection = get_mongo_collection("business_listings")

    def to_clean_dict(item):
        if isinstance(item, dict):
            return item
        return {k: v for k, v in vars(item).items() if not k.startswith("_")}

    if isinstance(listing_data, list):
        for item in listing_data:
            try:
                collection.insert_one(to_clean_dict(item))
            except DuplicateKeyError:
                pass
            except Exception as e:
                print("❌ Failed to insert listing into MongoDB:", e)
    elif isinstance(listing_data, dict):
        try:
            collection.insert_one(to_clean_dict(listing_data))
        except DuplicateKeyError:
            pass
        except Exception as e:
            print("❌ Failed to insert listing into MongoDB:", e)
    else:
        print("❌ Unsupported data format for MongoDB:", type(listing_data), listing_data)


# To extract seller details like seller name and contacts etc
async def extract_seller_details(page, listing):
    try:
        await page.goto(listing.url, timeout=60000, wait_until="load")
        await page.wait_for_selector("body")
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        try:
            # Get full HTML content
          # Grab entire page HTML
          html = await page.content()
          soup = BeautifulSoup(html, "html.parser")
      
          # Look for the hidden span that contains the phone number
          phone_container = soup.find("span", class_="ctc_phone", style=lambda s: s and "display:none" in s)
      
          if phone_container:
              # Find the phone number inside this hidden span
              phone_number_span = phone_container.find("span", class_="text-dec-h")
              if phone_number_span:
                  listing.seller_contact = phone_number_span.get_text(strip=True)
                  log.info(f"[✓] Found phone number: {listing.seller_contact}")
              else:
                  log.warning(f"[!] Hidden phone number span not found inside container at {listing.url}")
          else:
              log.warning(f"[!] Hidden phone container not found in HTML for {listing.url}")
      
        except Exception as e:
           log.warning(f"❌ Could not extract phone from HTML for {listing.url} — Reason: {str(e)}")

    
        # Extract Seller Name
        try:
            # Get all divs and scan for "Listed By:"
            divs = await page.locator("div").all()
            seller_name = None
            for div in divs:
                content = await div.inner_text()
                if "Listed By:" in content:
                    lines = [line.strip() for line in content.splitlines() if line.strip()]
                    for i, line in enumerate(lines):
                        if "Listed By:" in line and i + 1 < len(lines):
                            seller_name = lines[i + 1]
                            break
                    if seller_name:
                        break

            if seller_name:
                listing.seller_name = seller_name
                log.info(f"[✓] Seller name extracted: {seller_name}")
            else:
                log.warning("[!] Seller name not found in page content.")

        except Exception as e:
            log.error(f"[x] Timeout or error extracting seller name: {e}")

        # Title
        heading_element = soup.select_one("h1.bfsTitle")
        listing.name = heading_element.get_text(strip=True) if heading_element else "N/A"

        # Financials
        finance_string = ""
        financials = soup.select(".financials .row p")
        for item in financials:
            title = item.select_one(".title")
            value = item.select_one(".normal")
            if title and value:
                finance_string += f"{title.get_text()} {value.get_text()}\n"
        listing.financials = finance_string

        # Description
        description_elem = soup.select_one(".businessDescription")
        listing.description = description_elem.get_text(strip=True) if description_elem else ""

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
        log.info(f"[✓] Extracted seller info for: {listing.name}")

    except Exception as e:
        log.error(f"[x] Failed to extract details for {listing.name}: {e}")
        listing.blocked = True

    return listing


async def extract_listing_details(elements):
    business_listings = []

    for el in elements:
        try:
            href = await el.get_attribute("href")
            if href:
                listing_url = clean_url(href)
                listing_id = listing_url.split("/")[-1]
                contact_button_id = f"hlViewTelephone_{listing_id}"

                listing_obj = BusinessListing()
                listing_obj.url = listing_url
                listing_obj.listing_id = listing_id
                listing_obj.contact_button_id = contact_button_id

                business_listings.append(listing_obj)
        except Exception as e:
            log.error(f"Error extracting listing: {e}")

    return business_listings

# ----------------------------------------------------------------------------------


from playwright.async_api import async_playwright
import asyncio
import logging

log = logging.getLogger(__name__)

async def scrape_regions_with_play_wright(headless, use_proxy):
    browser = await get_play_chrome_browser(headless, use_proxy)
    response_data = None
    ajax_url_keyword = "api/Resource/GetRegions"

    try:
        # Create context and page from the browser
        context = await browser.new_context()
        page = await context.new_page()

        await block_images(page)
        await stealth_async(page)

        # Start waiting for the AJAX request
        async def wait_for_ajax():
            response = await page.wait_for_response(
                lambda r: (
                    r.request.resource_type in ["xhr", "fetch"] and
                    ajax_url_keyword in r.url and
                    r.status == 200
                ),
                timeout=15000
            )

            request = response.request
            request_details = {
                "method": request.method,
                "url": request.url,
                "headers": request.headers,
                "post_data": await request.post_data() if request.method != "GET" else None,
            }

            content_type = response.headers.get("content-type", "")
            response_body = (
                await response.json() if "application/json" in content_type else await response.text()
            )

            return {
                "request": request_details,
                "response": response_body,
            }

        # Navigate and simultaneously wait for AJAX
        ajax_future = asyncio.create_task(wait_for_ajax())
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        ajax_result = await ajax_future

        log.info("[✓] AJAX Request: %s", ajax_result["request"])
        log.info("[✓] AJAX Response: %s", ajax_result["response"])

        response_data = ajax_result["response"]

    except Exception as e:
        print(f"[!] Error capturing AJAX: {e}")
    finally:
        await browser.close()
        await browser._my_playwright.stop()

    return response_data

def clean_url(href: str) -> str:
    href = href.strip()

    # Remove accidental duplicate slashes but preserve protocol ones (e.g., 'https://')
    href = re.sub(r"(?<!:)//+", "/", href)


    return href
