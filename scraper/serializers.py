from rest_framework import serializers

class SellerDetailsSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.CharField()
    contact_button_id = serializers.CharField()
    seller_name = serializers.CharField()
    seller_contact = serializers.CharField()
    listing_id = serializers.CharField()
    financials = serializers.CharField()
    description = serializers.CharField()
    detailed_info = serializers.CharField()
    blocked = serializers.BooleanField()

  
# Partial serializer for initial listing extraction
class BusinessListingSerializer(serializers.Serializer):
    url = serializers.CharField()
    listing_id = serializers.CharField()
    contact_button_id = serializers.CharField()   

class RegionSerializer(serializers.Serializer):
    geoType = serializers.IntegerField()
    regionId = serializers.CharField()
    countryCode = serializers.CharField()
    countryId = serializers.CharField() 
    stateCode = serializers.CharField()
    legacyRegionId = serializers.IntegerField() 
    legacyRegionCode = serializers.CharField()
    metroAreaId = serializers.IntegerField()
    regionName = serializers.CharField()
    regionNameSeo = serializers.CharField()
    displayName = serializers.CharField() 
    locationDetected = serializers.BooleanField()    