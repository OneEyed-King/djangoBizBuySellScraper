from .views import ScraperView, SellerView
from django.urls import path

urlpatterns = [
    path("scrape/", ScraperView.as_view(), name="scrape-listing"),
    path("seller/", SellerView.as_view(), name="scrape-seller"),
]