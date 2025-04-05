from django.db import models

# apis/business_listing.py

class BusinessListing(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    contact_button_id = models.CharField(max_length=255)
    seller_name = models.CharField(max_length=255, blank=True, null=True)
    seller_contact = models.CharField(max_length=255, blank=True, null=True)
    listing_id = models.CharField(max_length=100, unique=True)
    financials = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    detailed_info = models.TextField(blank=True, null=True)
    blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name or self.listing_id


# Create your models here.
