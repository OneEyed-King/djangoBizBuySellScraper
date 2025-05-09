from .views import ExportScrapedData, PlayWrightSellerView, ScraperView, SellerView, PlayWrightRegionView
from django.urls import path

urlpatterns = [
    path("get-all-listings/", ScraperView.as_view(), name="scrape-listing"),
    path("get-listing-details/", SellerView.as_view(), name="scrape-seller"),
    path("play-listing-details/", PlayWrightSellerView.as_view(), name="scrape-seller-playwright"),
    path("play-regions/", PlayWrightRegionView.as_view(), name="scrape-regions-playwright"),
    path("export-listings/", ExportScrapedData.as_view(), name="export-scraped-data"),
]