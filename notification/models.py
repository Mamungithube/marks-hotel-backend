from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, EmailValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q, F
from decimal import Decimal
import uuid
from datetime import timedelta
from authontication.models import TimeStampedModel, SoftDeleteModel
from authontication.models import User
from booking_api.models import Booking

# ==========================================
# 8. NOTIFICATION & ACTIVITY LOG MODELS
# ==========================================

from authontication.models import SoftDeleteModel


class Notification(SoftDeleteModel):
    """
    User notifications
    """
    NOTIFICATION_TYPE_CHOICES = (
        ('booking_confirmed', _('Booking Confirmed')),
        ('payment_received', _('Payment Received')),
        ('check_in_reminder', _('Check-in Reminder')),
        ('check_out_reminder', _('Check-out Reminder')),
        ('review_request', _('Review Request')),
        ('promotional', _('Promotional')),
        ('system', _('System')),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related object (generic)
    related_booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Status
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()




# ==========================================
# 9. ADDITIONAL UTILITY MODELS
# ==========================================

class PromoCode(SoftDeleteModel):
    """
    Discount promo codes
    """
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_("Unique promo code")
    )
    description = models.TextField(blank=True)
    
    # Discount details
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage'
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Maximum discount amount for percentage type")
    )
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Total number of times this code can be used")
    )
    usage_per_user = models.PositiveIntegerField(
        default=1,
        help_text=_("Times each user can use this code")
    )
    used_count = models.PositiveIntegerField(default=0)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Minimum booking amount
    min_booking_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('promo code')
        verbose_name_plural = _('promo codes')
        db_table = 'promo_codes'
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]
    
    def __str__(self):
        return self.code
    
    @property
    def is_valid(self):
        """Check if promo code is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True


class SiteSettings(models.Model):
    """
    Global site settings - একটাই entry থাকবে
    """
    hotel_name = models.CharField(max_length=200, default='Grand Hotel')
    hotel_email = models.EmailField()
    hotel_phone = models.CharField(max_length=15)
    hotel_address = models.TextField()
    
    # Tax settings
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Booking settings
    min_booking_days = models.PositiveIntegerField(default=1)
    max_booking_days = models.PositiveIntegerField(default=30)
    advance_booking_days = models.PositiveIntegerField(
        default=365,
        help_text=_("How many days in advance can guests book")
    )
    
    # Cancellation policy
    free_cancellation_hours = models.PositiveIntegerField(
        default=24,
        help_text=_("Hours before check-in for free cancellation")
    )
    cancellation_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Check-in/out times
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='12:00')
    
    # Social links
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('site settings')
        verbose_name_plural = _('site settings')
        db_table = 'site_settings'
    
    def __str__(self):
        return self.hotel_name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
