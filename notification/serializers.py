# notification/serializers.py
# ==========================================

from rest_framework import serializers
from notification.models import Notification, PromoCode, SiteSettings


class NotificationSerializer(serializers.ModelSerializer):
    """Notification Serializer"""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    booking_number = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'title', 'message',
            'related_booking', 'booking_number',
            'is_read', 'read_at',
            'sent_via_email', 'sent_via_sms',
            'created_at'
        ]
        read_only_fields = [
            'id', 'is_read', 'read_at', 'created_at'
        ]
    
    def get_booking_number(self, obj):
        if obj.related_booking:
            return obj.related_booking.booking_number
        return None


class PromoCodeSerializer(serializers.ModelSerializer):
    """Promo Code Serializer"""
    discount_type_display = serializers.CharField(
        source='get_discount_type_display',
        read_only=True
    )
    is_valid_status = serializers.BooleanField(
        source='is_valid',
        read_only=True
    )
    
    class Meta:
        model = PromoCode
        fields = [
            'id', 'code', 'description',
            'discount_type', 'discount_type_display',
            'discount_value', 'max_discount_amount',
            'usage_limit', 'usage_per_user', 'used_count',
            'valid_from', 'valid_until',
            'min_booking_amount',
            'is_valid_status', 'is_active'
        ]
        read_only_fields = ['id', 'used_count']


class PromoCodeValidationSerializer(serializers.Serializer):
    """Promo Code Validation Serializer"""
    code = serializers.CharField(required=True)
    booking_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True
    )
    
    def validate(self, attrs):
        """Validate promo code"""
        code = attrs['code'].upper()
        booking_amount = attrs['booking_amount']
        
        try:
            promo = PromoCode.objects.get(code=code, is_active=True)
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError({
                'code': 'Invalid promo code.'
            })
        
        if not promo.is_valid:
            raise serializers.ValidationError({
                'code': 'This promo code has expired or reached its usage limit.'
            })
        
        if promo.min_booking_amount and booking_amount < promo.min_booking_amount:
            raise serializers.ValidationError({
                'code': f'Minimum booking amount is ${promo.min_booking_amount}.'
            })
        
        # Calculate discount
        if promo.discount_type == 'percentage':
            discount = booking_amount * (promo.discount_value / 100)
            if promo.max_discount_amount:
                discount = min(discount, promo.max_discount_amount)
        else:
            discount = promo.discount_value
        
        attrs['promo'] = promo
        attrs['discount_amount'] = discount
        return attrs


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Site Settings Serializer"""
    
    class Meta:
        model = SiteSettings
        fields = [
            'hotel_name', 'hotel_email', 'hotel_phone', 'hotel_address',
            'tax_percentage',
            'min_booking_days', 'max_booking_days', 'advance_booking_days',
            'free_cancellation_hours', 'cancellation_fee_percentage',
            'check_in_time', 'check_out_time',
            'facebook_url', 'instagram_url', 'twitter_url',
            'meta_title', 'meta_description',
            'updated_at'
        ]
        read_only_fields = ['updated_at']