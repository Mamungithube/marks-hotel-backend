# booking_api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    RoomType, Room, Amenity, 
    RoomAmenity, Booking
)
from django.utils import timezone
from datetime import timedelta

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'

# class RoomImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RoomImage
#         fields = ['id', 'is_primary']

class RoomTypeSerializer(serializers.ModelSerializer):
    # images = RoomImageSerializer(many=True, read_only=True)
    amenities = serializers.SerializerMethodField()
    available_rooms = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomType
        fields = ['id', 'name', 'description', 'price_per_night', 'amenities', 'available_rooms']
    
    def get_amenities(self, obj):
        room_amenities = RoomAmenity.objects.filter(room_type=obj)
        return AmenitySerializer([ra.amenity for ra in room_amenities], many=True).data
    
    def get_available_rooms(self, obj):
        # Get query parameters for date range
        request = self.context.get('request')
        if request:
            check_in = request.query_params.get('check_in')
            check_out = request.query_params.get('check_out')
            
            if check_in and check_out:
                # Find rooms of this type that are not booked in the given date range
                booked_rooms = Booking.objects.filter(
                    room__room_type=obj,
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in,
                    status__in=['pending', 'confirmed']
                ).values_list('room__id', flat=True)
                
                available_rooms = Room.objects.filter(room_type=obj).exclude(id__in=booked_rooms)
                return RoomSerializer(available_rooms, many=True).data
        
        # If no dates provided, return all rooms of this type
        return RoomSerializer(obj.rooms.all(), many=True).data

class RoomSerializer(serializers.ModelSerializer):
    room_type_name = serializers.ReadOnlyField(source='room_type.name')
    price_per_night = serializers.ReadOnlyField(source='room_type.price_per_night')
    
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'room_type_name', 'capacity', 
                  'size', 'floor', 'has_view', 'has_balcony', 'price_per_night']

class BookingSerializer(serializers.ModelSerializer):
    room_details = RoomSerializer(source='room', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)

    user = serializers.ReadOnlyField(source='user.username')
    room_type = serializers.ReadOnlyField(source='room.room_type.name')  # ✅ সঠিক source ব্যবহার
    
    class Meta:
        model = Booking
        fields = ['id', 'user', 'user_details', 'room', 'room_details', 
                  'room_type',  # ✅ এখানে যোগ করুন
                  'check_in_date', 'check_out_date', 'adults', 'children',
                  'booking_date', 'status', 'special_requests']
        read_only_fields = ['booking_date', 'status','payment_status', 'stripe_payment_intent']
