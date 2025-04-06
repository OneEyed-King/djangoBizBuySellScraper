from .views import ScraperView, SellerView
from django.urls import path

urlpatterns = [
    path("get-all-listings/", ScraperView.as_view(), name="scrape-listing"),
    path("get-listing-details/", SellerView.as_view(), name="scrape-seller"),
]