import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import logging
from scraper.utils.web_driver_factory import get_camoufox_browser

from .models import BusinessListing

URL = 'https://www.bizbuysell.com/buy/'
log = logging.getLogger(__name__)


async def scrape_with_play_wright(headless, count, skip):
    return await scrape_data(headless, count, skip)


async def scrape_data(headless, count, skip):
    async with async_playwright() as p:
        browser = await get_camoufox_browser(headless)
        page = await browser.new_page()

        await page.goto(URL)
        await page.wait_for_selector("a.diamond")
        elements = await page.query_selector_all("a.diamond")

        log.info('Number of Listings found: %s', len(elements))
        web_listings = await extract_listing_details(elements)

        if skip > len(web_listings):
            skip = 0
        web_listings = web_listings[skip:]
        business_listings = []

        limited_listings = web_listings[:min(count, len(web_listings))]
        tasks = [extract_seller_details_threaded(p, listing, headless) for listing in limited_listings]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result and result.description:
                business_listings.append(result)

        await browser.close()
        return business_listings


async def extract_seller_details_threaded(playwright, listing, headless):
    browser = await get_camoufox_browser(headless)
    page = await browser.new_page()
    try:
        return await extract_seller_details(page, listing)
    finally:
        await browser.close()


async def extract_seller_details(page, listing):
    try:
        await page.goto(listing.url)
        await page.wait_for_selector("body")
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Click contact button
        try:
            contact_button = await page.wait_for_selector(f"#{listing.contact_button_id}", timeout=5000)
            await contact_button.click()
            await page.wait_for_timeout(2000)

            phone_elem = await page.wait_for_selector(f"#lblViewTpnTelephone_{listing.listing_id}", timeout=5000)
            listing.seller_contact = await phone_elem.inner_text()
        except:
            log.warning(f"Could not get phone for {listing.url}")

        # # Seller Name
        # try:
            
        #     # seller_elem = await page.wait_for_selector("#contactSellerForm > div:nth-child(10) > div:nth-child(1) > div:nth-child(1)", timeout=10000)
        #     seller_elem = await page.wait_for_selector("div:has-text('Listed By:')", timeout=10000)
        #     raw_text = await seller_elem.inner_text()
        #     log.info('raw text seller name %s', raw_text)
        #     listing.seller_name = raw_text.replace("Listed By:", "").strip()
        # except:
        #     log.error("Timeout for seller name")
        #     pass

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
                listing_url = href.rstrip("/")
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
