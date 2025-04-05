from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
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
