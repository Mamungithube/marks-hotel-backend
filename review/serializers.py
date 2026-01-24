# from rest_framework import serializers
# from . import models

# class ReviewSerializer(serializers.ModelSerializer):
#     reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)

#     class Meta:
#         model = models.Review
#         fields = ['id', 'body', 'created', 'rating', 'reviewer', 'reviewer_name']
#         extra_kwargs = {'reviewer': {'required': False}}  # Allow it to be auto-set

#     def create(self, validated_data):
#         validated_data['reviewer'] = self.context['request'].user
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         validated_data['reviewer'] = instance.reviewer  # Prevent reviewer change
#         return super().update(instance, validated_data)

# class ContactUsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.ContactUs
#         fields = '__all__'



# review/serializers.py
# ==========================================

from rest_framework import serializers
from .models import Review, ContactMessage
from authontication.serializers import UserSerializer
from booking_api.serializers import BookingListSerializer


class ReviewSerializer(serializers.ModelSerializer):
    """Review Serializer"""
    user = UserSerializer(read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    booking_number = serializers.CharField(
        source='booking.booking_number',
        read_only=True
    )
    overall_rating_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'booking_number', 'user', 'user_name',
            'overall_rating', 'overall_rating_display',
            'cleanliness_rating', 'service_rating', 'value_rating',
            'title', 'comment',
            'is_verified', 'is_approved',
            'helpful_count', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'is_verified', 'is_approved',
            'helpful_count', 'created_at'
        ]
    
    def get_overall_rating_display(self, obj):
        return '⭐' * obj.overall_rating


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Review Creation Serializer"""
    booking_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Review
        fields = [
            'booking_id', 'overall_rating',
            'cleanliness_rating', 'service_rating', 'value_rating',
            'title', 'comment'
        ]
    
    def validate_booking_id(self, value):
        """Validate booking"""
        from booking_api.models import Booking
        user = self.context['request'].user
        
        try:
            booking = Booking.objects.get(id=value, user=user)
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Invalid booking.")
        
        # Check if booking is completed
        if booking.booking_status != 'checked_out':
            raise serializers.ValidationError(
                "You can only review completed bookings."
            )
        
        # Check if already reviewed
        if Review.objects.filter(booking=booking, user=user).exists():
            raise serializers.ValidationError(
                "You have already reviewed this booking."
            )
        
        return value
    
    def create(self, validated_data):
        """Create review"""
        from booking_api.models import Booking
        booking = Booking.objects.get(id=validated_data.pop('booking_id'))
        
        review = Review.objects.create(
            booking=booking,
            user=self.context['request'].user,
            **validated_data
        )
        return review


class ContactMessageSerializer(serializers.ModelSerializer):
    """Contact Message Serializer"""
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    assigned_to_name = serializers.SerializerMethodField()
    responded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'message',
            'user', 'priority', 'priority_display',
            'status', 'status_display',
            'assigned_to', 'assigned_to_name',
            'response', 'responded_at',
            'responded_by', 'responded_by_name',
            'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'assigned_to',
            'response', 'responded_at', 'responded_by',
            'created_at'
        ]
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None
    
    def get_responded_by_name(self, obj):
        if obj.responded_by:
            return obj.responded_by.get_full_name()
        return None


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Contact Message Creation Serializer"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
    
    def create(self, validated_data):
        """Create contact message"""
        user = self.context['request'].user
        
        # Link to user if authenticated
        if user.is_authenticated:
            validated_data['user'] = user
        
        return ContactMessage.objects.create(**validated_data)
