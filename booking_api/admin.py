# booking_api/admin.py

from django.contrib import admin
from .models import (
    RoomType, Room, Amenity, 
    RoomAmenity, Booking
)

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_night')
    search_fields = ('name',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'capacity', 'floor')
    list_filter = ('room_type', 'capacity', 'floor', 'has_view', 'has_balcony')
    search_fields = ('room_number',)

# @admin.register(RoomImage)
# class RoomImageAdmin(admin.ModelAdmin):
#     list_display = ('room_type', 'is_primary')
#     list_filter = ('room_type', 'is_primary')

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(RoomAmenity)
class RoomAmenityAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'amenity')
    list_filter = ('room_type', 'amenity')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room', 'check_in_date', 'check_out_date', 'status')
    list_filter = ('status', 'check_in_date', 'check_out_date')
    search_fields = ('user__username', 'room__room_number')
    date_hierarchy = 'booking_date'



