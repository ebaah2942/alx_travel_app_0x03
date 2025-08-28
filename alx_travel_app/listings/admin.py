from django.contrib import admin

from .models import Listing, Booking, Review

# Register your models here.

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price_per_night', 'created_at')
    search_fields = ('title', 'location')
    list_filter = ('location', 'created_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('listing', 'guest_name', 'check_in', 'check_out', 'created_at')
    search_fields = ('guest_name', 'listing__title')
    list_filter = ('check_in', 'check_out', 'created_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):    
    list_display = ('listing', 'reviewer_name', 'rating', 'created_at')
    search_fields = ('reviewer_name', 'listing__title')
    list_filter = ('rating', 'created_at')
