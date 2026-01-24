# # booking_api/serializers.py

# from rest_framework import serializers
# from django.contrib.auth.models import User
# from .models import (
#     RoomType, Room, Amenity, 
#     RoomAmenity, Booking
# )
# from django.utils import timezone
# from datetime import timedelta

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'first_name', 'last_name']

# class AmenitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Amenity
#         fields = '__all__'

# # class RoomImageSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = RoomImage
# #         fields = ['id', 'is_primary']

# class RoomTypeSerializer(serializers.ModelSerializer):
#     # images = RoomImageSerializer(many=True, read_only=True)
#     amenities = serializers.SerializerMethodField()
#     available_rooms = serializers.SerializerMethodField()
    
#     class Meta:
#         model = RoomType
#         fields = ['id', 'name', 'description', 'price_per_night', 'amenities', 'available_rooms']
    
#     def get_amenities(self, obj):
#         room_amenities = RoomAmenity.objects.filter(room_type=obj)
#         return AmenitySerializer([ra.amenity for ra in room_amenities], many=True).data
    
#     def get_available_rooms(self, obj):
#         # Get query parameters for date range
#         request = self.context.get('request')
#         if request:
#             check_in = request.query_params.get('check_in')
#             check_out = request.query_params.get('check_out')
            
#             if check_in and check_out:
#                 # Find rooms of this type that are not booked in the given date range
#                 booked_rooms = Booking.objects.filter(
#                     room__room_type=obj,
#                     check_in_date__lt=check_out,
#                     check_out_date__gt=check_in,
#                     status__in=['pending', 'confirmed']
#                 ).values_list('room__id', flat=True)
                
#                 available_rooms = Room.objects.filter(room_type=obj).exclude(id__in=booked_rooms)
#                 return RoomSerializer(available_rooms, many=True).data
        
#         # If no dates provided, return all rooms of this type
#         return RoomSerializer(obj.rooms.all(), many=True).data

# class RoomSerializer(serializers.ModelSerializer):
#     room_type_name = serializers.ReadOnlyField(source='room_type.name')
#     price_per_night = serializers.ReadOnlyField(source='room_type.price_per_night')
    
#     class Meta:
#         model = Room
#         fields = ['id', 'room_number', 'room_type', 'room_type_name', 'capacity', 
#                   'size', 'floor', 'has_view', 'has_balcony', 'price_per_night']

# class BookingSerializer(serializers.ModelSerializer):
#     room_details = RoomSerializer(source='room', read_only=True)
#     user_details = UserSerializer(source='user', read_only=True)

#     user = serializers.ReadOnlyField(source='user.username')
#     room_type = serializers.ReadOnlyField(source='room.room_type.name')  # ✅ সঠিক source ব্যবহার
    
#     class Meta:
#         model = Booking
#         fields = ['id', 'user', 'user_details', 'room', 'room_details', 
#                   'room_type',  # ✅ এখানে যোগ করুন
#                   'check_in_date', 'check_out_date', 'adults', 'children',
#                   'booking_date', 'status', 'special_requests']
#         read_only_fields = ['booking_date', 'status','payment_status', 'stripe_payment_intent']




# booking_api/serializers.py
# ==========================================

from rest_framework import serializers
from .models import Booking, Payment
from room_management.serializers import RoomSerializer
from authontication.serializers import UserSerializer
from decimal import Decimal
from datetime import date


class PaymentSerializer(serializers.ModelSerializer):
    """
    Payment Serializer
    """
    booking_number = serializers.CharField(
        source='booking.booking_number',
        read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    payment_type_display = serializers.CharField(
        source='get_payment_type_display',
        read_only=True
    )
    
    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'booking', 'booking_number',
            'amount', 'payment_method', 'payment_method_display',
            'payment_type', 'payment_type_display',
            'stripe_payment_intent_id', 'stripe_charge_id',
            'is_successful', 'failure_reason',
            'payment_date', 'notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'payment_date',
            'created_at'
        ]


class BookingListSerializer(serializers.ModelSerializer):
    """
    Booking List Serializer - for list view
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    room_type = serializers.CharField(source='room.room_type.name', read_only=True)
    booking_status_display = serializers.CharField(
        source='get_booking_status_display',
        read_only=True
    )
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )
    nights = serializers.IntegerField(source='number_of_nights', read_only=True)
    balance = serializers.DecimalField(
        source='balance_amount',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_number', 'user_name', 'user_email',
            'room_number', 'room_type',
            'check_in_date', 'check_out_date', 'nights',
            'adults', 'children',
            'booking_status', 'booking_status_display',
            'payment_status', 'payment_status_display',
            'total_amount', 'paid_amount', 'balance',
            'created_at'
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Booking Detail Serializer - for detail view
    """
    user = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    cancelled_by_name = serializers.SerializerMethodField()
    nights = serializers.IntegerField(source='number_of_nights', read_only=True)
    balance = serializers.DecimalField(
        source='balance_amount',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    is_cancellable_status = serializers.BooleanField(
        source='is_cancellable',
        read_only=True
    )
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_number', 'user', 'room',
            'check_in_date', 'check_out_date', 'nights',
            'actual_check_in', 'actual_check_out',
            'adults', 'children',
            'booking_status', 'payment_status',
            'base_amount', 'tax_amount', 'discount_amount',
            'total_amount', 'paid_amount', 'balance',
            'special_requests', 'internal_notes',
            'stripe_payment_intent_id', 'stripe_customer_id',
            'cancelled_at', 'cancelled_by', 'cancelled_by_name',
            'cancellation_reason', 'refund_amount',
            'is_cancellable_status', 'payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'booking_number', 'created_at', 'updated_at',
            'cancelled_at', 'actual_check_in', 'actual_check_out'
        ]
    
    def get_cancelled_by_name(self, obj):
        if obj.cancelled_by:
            return obj.cancelled_by.get_full_name()
        return None


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Booking Creation Serializer
    """
    room_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'room_id', 'check_in_date', 'check_out_date',
            'adults', 'children', 'special_requests'
        ]
    
    def validate(self, attrs):
        """Validate booking data"""
        check_in = attrs['check_in_date']
        check_out = attrs['check_out_date']
        
        # Check dates
        if check_in < date.today():
            raise serializers.ValidationError({
                'check_in_date': 'Check-in date cannot be in the past.'
            })
        
        if check_out <= check_in:
            raise serializers.ValidationError({
                'check_out_date': 'Check-out date must be after check-in date.'
            })
        
        # Check room availability
        from room_management.models import Room
        try:
            room = Room.objects.get(id=attrs['room_id'], is_active=True)
        except Room.DoesNotExist:
            raise serializers.ValidationError({
                'room_id': 'Invalid room selected.'
            })
        
        if not room.is_available:
            raise serializers.ValidationError({
                'room_id': 'Selected room is not available.'
            })
        
        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            room=room,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
            booking_status__in=['pending', 'confirmed', 'checked_in'],
            is_active=True
        ).exists()
        
        if overlapping:
            raise serializers.ValidationError({
                'room_id': 'Room is already booked for selected dates.'
            })
        
        # Check occupancy
        total_guests = attrs['adults'] + attrs['children']
        if total_guests > room.room_type.max_occupancy:
            raise serializers.ValidationError({
                'adults': f'Total guests exceed room capacity of {room.room_type.max_occupancy}.'
            })
        
        attrs['room'] = room
        return attrs
    
    def create(self, validated_data):
        """Create booking with calculated prices"""
        room = validated_data.pop('room')
        room_id = validated_data.pop('room_id')
        
        # Calculate number of nights
        nights = (validated_data['check_out_date'] - validated_data['check_in_date']).days
        
        # Calculate base amount
        base_amount = room.room_type.base_price * nights
        
        # Calculate tax (from site settings or default 10%)
        from notification.models import SiteSettings
        settings = SiteSettings.get_settings()
        tax_rate = settings.tax_percentage / 100
        tax_amount = base_amount * Decimal(str(tax_rate))
        
        # Create booking
        booking = Booking.objects.create(
            user=self.context['request'].user,
            room=room,
            base_amount=base_amount,
            tax_amount=tax_amount,
            total_amount=base_amount + tax_amount,
            **validated_data
        )
        
        # Update room status
        room.current_status = 'reserved'
        room.save()
        
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """
    Booking Update Serializer - limited fields
    """
    class Meta:
        model = Booking
        fields = [
            'special_requests', 'internal_notes'
        ]


class BookingCancellationSerializer(serializers.Serializer):
    """
    Booking Cancellation Serializer
    """
    cancellation_reason = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate cancellation"""
        booking = self.instance
        
        if not booking.is_cancellable:
            raise serializers.ValidationError(
                "This booking cannot be cancelled."
            )
        
        return attrs