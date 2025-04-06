# BizBuySell Scraper API

This project is a web scraper for BizBuySell, a website for buying and selling businesses. It uses Python, Django, and Selenium to extract data from BizBuySell listings.

**Framework and Libraries Used:**
* **Django:** 4.2.1
* **Selenium:** 4.10.0
* **Python:** 3.11


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
