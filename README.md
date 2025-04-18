# BizBuySell Scraper API

This project is a web scraper for BizBuySell, a website for buying and selling businesses. It uses Python, Django, and Playwright to extract data from BizBuySell listings and stores them in MongoDB.

**Framework and Libraries Used:**
* **Django:** 4.2.1
* **Playwright:** 1.32.0
* **Python:** 3.11
* **MongoDB:** 4.4.0

**New Features:**

* **Playwright API Integration:** The scraper now uses the Playwright API for improved performance, reliability, and stealth capabilities.
* **Stealth Enhancements:** Implemented various techniques, including browser camouflage, to bypass bot detection mechanisms.
* **Proxy Rotation and Retry Mechanism:** Added proxy rotation and retry mechanism for increased resilience and to avoid IP blocking.  If you have proxies, add them to the `.env` file in the `scraper` directory in the following format: `PROXIES=user:password@ip:port,user:password@ip:port`.


**Additional Information:**

* **Default Browser:** Chrome is the default browser used for scraping.


This project provides an API for scraping data from BizBuySell.

## Endpoints

### Get All Listings

**URL:** `/get-all-listings/`

**Method:** `GET`

**Parameters:**

- `headless` (optional): Boolean. Whether to run the scraper in headless mode. Defaults to `false`.

**Response:**

```json
[
  {
    "url": "string",
    "listing_id": "string",
    "contact_button_id": "string"
  }
]
```

### Get Listing Details

**URL:** `/get-listing-details/`

**Method:** `GET`

**Parameters:**

- `headless` (optional): Boolean. Whether to run the scraper in headless mode. Defaults to `false`.
- `count` (optional): Integer. The number of listings to scrape. Defaults to 2.
- `skip` (optional): Integer. The number of listings to skip. Defaults to 0.

**Response:**

```json
[
  {
    "name": "string",
    "url": "string",
    "contact_button_id": "string",
    "seller_name": "string",
    "seller_contact": "string",
    "listing_id": "string",
    "financials": "string",
    "description": "string",
    "detailed_info": "string",
    "blocked": true
  }
]

### Get Playwright Listing Details

**URL:** `/play-listing-details/`

**Method:** `GET`

**Parameters:**

- `headless` (optional): Boolean. Whether to run the scraper in headless mode. Defaults to `false`.
- `count` (optional): Integer. The number of listings to scrape. Defaults to 2.
- `skip` (optional): Integer. The number of listings to skip. Defaults to 0.

**Response:**

```json
[
  {
    "name": "string",
    "url": "string",
    "contact_button_id": "string",
    "seller_name": "string",
    "seller_contact": "string",
    "listing_id": "string",
    "financials": "string",
    "description": "string",
    "detailed_info": "string",
    "blocked": true
  }
]
