from django.contrib import admin
# Register your models here.

from .models import RoomType,Amenity,RoomTypeAmenity,Room

admin.site.register(RoomType)
admin.site.register(Amenity)
admin.site.register(RoomTypeAmenity)
admin.site.register(Room)
