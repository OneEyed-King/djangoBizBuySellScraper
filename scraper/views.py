from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import asyncio

from scraper.playwright_scraper import scrape_with_play_wright
from .scraper import extract_listing_details, scrape, get_listings
from .serializers import BusinessListingSerializer, SellerDetailsSerializer

class ScraperView(APIView):
   def get(self, request):

    headless = request.GET.get('headless', 'false').lower() == 'true'  # default: False
    
    scraped_data = get_listings(headless)
    serializer = BusinessListingSerializer(scraped_data, many= True)
    return Response(serializer.data)
   
class SellerView(APIView):
  def get(self, request):
    headless = request.GET.get('headless', 'false').lower() == 'true'  # default: False
    count = int(request.GET.get('count', 2))                           # default: 5
    skip = int(request.GET.get('skip', 0))                             # default: 0
    scraped_data = scrape(headless, count, skip)
    serializer = SellerDetailsSerializer(scraped_data, many = True) 
    return Response(serializer.data)  
  
class PlayWrightSellerView(APIView):
  def get(self, request):
    headless = request.GET.get('headless', 'false').lower() == 'true'  # default: False
    count = int(request.GET.get('count', 2))                           # default: 5
    skip = int(request.GET.get('skip', 0))                             # default: 0
    use_proxy = request.GET.get('use_proxy', 'false').lower() == 'true'  # default: False

    scraped_data = asyncio.run(scrape_with_play_wright(headless, count, skip, use_proxy))
    serializer = SellerDetailsSerializer(scraped_data, many = True) 
    return Response(serializer.data)    
