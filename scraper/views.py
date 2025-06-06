from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import asyncio

from scraper.playwright_scraper import export_business_csv, export_business_data, scrape_with_play_wright, scrape_regions_with_play_wright
from .scraper import extract_listing_details, scrape, get_listings
from .serializers import BusinessListingSerializer, SellerDetailsSerializer, RegionSerializer

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

class PlayWrightRegionView(APIView):
    def get(self, request):
        try:
            headless = request.GET.get('headless', 'false').lower() == 'true'  # default: False
            use_proxy = request.GET.get('use_proxy', 'false').lower() == 'true'  # default: False

            # Run the async scraping function
            scraped_data = asyncio.run(scrape_regions_with_play_wright(headless, use_proxy))

            # Ensure the scraped data is in the correct format
            if scraped_data and isinstance(scraped_data, dict) and "value" in scraped_data:
                # Serialize the list of regions from the "value" key
                regions = scraped_data["value"]
                serializer = RegionSerializer(regions, many=True)
                return Response(serializer.data)

            return Response({"error": "No data found or unexpected response format"}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500) 
  
class ExportScrapedData(APIView):
    def get(self, request):
        # headless = request.GET.get('headless', 'false').lower() == 'true'
        # use_proxy = request.GET.get('use_proxy', 'false').lower() == 'true'

        # Await the async export function
        return  export_business_data(request)  # Should be an HttpResponse
    
class ExportScrapedDataAsCSV(APIView):
    def get(self, request):
        # headless = request.GET.get('headless', 'false').lower() == 'true'
        # use_proxy = request.GET.get('use_proxy', 'false').lower() == 'true'

        # Await the async export function
        return  export_business_csv(request)  # Should be an HttpResponse    
