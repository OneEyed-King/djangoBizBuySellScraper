# BizBuySell Scraper API

This project is a web scraper for BizBuySell, a website for buying and selling businesses. It uses Python, Django, and Playwright to extract data from BizBuySell listings and stores them in MongoDB.

---

## 🔧 Technologies Used

* **Python** 3.11
* **Django** 4.2.1
* **Playwright** 1.32.0
* **MongoDB** 4.4.0
* **BeautifulSoup** (for HTML parsing)
* **Playwright Stealth** (for bot evasion)

---

## 🚀 Key Features

* **Playwright API Integration**: Headless browser scraping with dynamic rendering support.
* **Stealth Mode**: Reduces bot detection via Playwright stealth techniques.
* **Proxy Rotation & Retry Logic**: Helps avoid IP blocking.
* **Region Extraction**: Captures region data via intercepted AJAX calls.
* **CSV & ZIP Export**: Export scraped listings as JSON+HTML or as CSV.
* **Django REST API**: Clean and modular structure with API endpoints.

> 💡 Add your proxy list in `.env` using:
>
> ```
> PROXIES=user:pass@ip:port,user:pass@ip:port,...
> ```

---

## 📱 API Endpoints

### 🔹 1. **Get All Listings**

**URL:** `/get-all-listings/`
**Method:** `GET`
**Parameters:**

* `headless` (optional): `true` or `false` (default: `false`)

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

---

### 🔹 2. **Get Listing Details (Selenium-based)**

**URL:** `/get-listing-details/`
**Method:** `GET`
**Parameters:**

* `headless` (optional): `true` or `false`
* `count` (optional): Number of listings to scrape (default: `2`)
* `skip` (optional): Number of listings to skip (default: `0`)

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
```

---

### 🔹 3. **Get Listing Details (Playwright-based)**

**URL:** `/play-listing-details/`
**Method:** `GET`
**Parameters:**

* `headless` (optional): `true` or `false`
* `use_proxy` (optional): `true` or `false`
* `count` (optional): Number of listings to scrape (default: `2`)
* `skip` (optional): Number of listings to skip (default: `0`)

**Response:** Same as the Selenium-based version above.

---

### 🔹 4. **Get Regions (Playwright - Intercepted Network Response)**

**URL:** `/play-regions/`
**Method:** `GET`
**Parameters:**

* `headless` (optional): `true` or `false`
* `use_proxy` (optional): `true` or `false`

**Response:**

```json
[
  {
    "geoType": 20,
    "regionId": "5",
    "countryCode": "US",
    "stateCode": "CA",
    "regionName": "California"
  }
]
```

---

### 🔹 5. **Export Listings as JSON + HTML ZIP**

**URL:** `/export-listings/`
**Method:** `GET`
**Returns:**

* A ZIP file download (`business_data.zip`) containing:

  * `data.json`: Complete JSON data from MongoDB
  * `*.html`: Individual raw HTML files per listing

---

### 🔹 6. **Export Listings as CSV**

**URL:** `/api/export/csv/`
**Method:** `GET`
**Returns:**

* A downloadable CSV file (`business_listings.csv`) containing:

```csv
name,url,seller_name,seller_contact,asking_price,cash_flow,description
"ABC Bakery","https://...","John Doe","123-456-7890","450,000","175,000","Profitable bakery"
```

---

## 🔪 Local Development

Start Django server:

```bash
poetry run python manage.py runserver
```

Test endpoints:

```bash
curl http://localhost:8000/api/export/csv/ --output listings.csv
```

---

## 🚼 Notes

* All data is saved to MongoDB (`business_listings` collection).
* The `.zip` export cleans up temporary files after the response is sent.
* CSV financials (`asking_price`, `cash_flow`) are parsed using regex from raw text.

---

## 📁 Project Structure

```
scraper/
│
├── views.py                # All Django API endpoints
├── playwright_scraper.py   # Core Playwright scraping logic
├── serializers.py          # DRF serializers for listing/region models
├── urls.py                 # Route definitions
├── utils/                  # Utility modules like MongoDB access
```

---

## 📅 Want to Extend?

* Add filters like `/api/export/csv/?state=CA`
* Schedule the scraper using Celery or cron
* Store raw JSON snapshots per listing

---

## 📃 License

MIT or custom – add your own if needed.
