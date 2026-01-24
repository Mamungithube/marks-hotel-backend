# booking_api /models.py
# ==========================================

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
from room_management.models import Room



# ==========================================
# 4. BOOKING MANAGEMENT MODELS
# ==========================================

class Booking(SoftDeleteModel):
    """
    Booking records - main booking model
    """
    BOOKING_STATUS_CHOICES = (
        ('pending', _('Pending Payment')),
        ('confirmed', _('Confirmed')),
        ('checked_in', _('Checked In')),
        ('checked_out', _('Checked Out')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('partial', _('Partially Paid')),
        ('paid', _('Paid')),
        ('refunded', _('Refunded')),
        ('failed', _('Failed')),
    )

    # Basic info
    booking_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    # Dates
    check_in_date = models.DateField(_('check-in date'), db_index=True)
    check_out_date = models.DateField(_('check-out date'), db_index=True)
    actual_check_in = models.DateTimeField(null=True, blank=True)
    actual_check_out = models.DateTimeField(null=True, blank=True)

    # Guests
    adults = models.PositiveIntegerField(
        _('number of adults'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    children = models.PositiveIntegerField(
        _('number of children'),
        default=0,
        validators=[MinValueValidator(0)]
    )

    # Status
    booking_status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    # Pricing
    base_amount = models.DecimalField(
        _('base amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        _('tax amount'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        _('discount amount'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    paid_amount = models.DecimalField(
        _('paid amount'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Special requests
    special_requests = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    # Payment integration
    stripe_payment_intent_id = models.CharField(
        max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(
        max_length=255, blank=True, null=True)

    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_bookings'
    )
    cancellation_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(
        _('refund amount'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        verbose_name = _('booking')
        verbose_name_plural = _('bookings')
        db_table = 'bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_number']),
            models.Index(fields=['user', 'booking_status']),
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['room', 'booking_status']),
            models.Index(fields=['payment_status', 'booking_status']),
        ]

    def __str__(self):
        return f"{self.booking_number} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        # Auto-generate booking number
        if not self.booking_number:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.booking_number = f"BK{timestamp}{self.id or ''}"

        # Calculate total amount
        self.total_amount = (
            self.base_amount +
            self.tax_amount -
            self.discount_amount
        )

        super().save(*args, **kwargs)

    @property
    def number_of_nights(self):
        """Calculate number of nights"""
        return (self.check_out_date - self.check_in_date).days

    @property
    def is_cancellable(self):
        """Check if booking can be cancelled"""
        if self.booking_status in ['cancelled', 'checked_out', 'no_show']:
            return False
        # Can't cancel if check-in is today or passed
        return self.check_in_date > timezone.now().date()

    @property
    def balance_amount(self):
        """Remaining amount to be paid"""
        return self.total_amount - self.paid_amount


class Payment(SoftDeleteModel):
    """
    Payment transactions - প্রতিটা payment track করবে
    """
    PAYMENT_METHOD_CHOICES = (
        ('stripe', _('Stripe')),
        ('cash', _('Cash')),
        ('bank_transfer', _('Bank Transfer')),
        ('cheque', _('Cheque')),
    )

    PAYMENT_TYPE_CHOICES = (
        ('booking', _('Booking Payment')),
        ('additional', _('Additional Charges')),
        ('refund', _('Refund')),
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        db_index=True
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    amount = models.DecimalField(
        _('payment amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='stripe'
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        default='booking'
    )

    # Stripe specific
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)

    # Status
    is_successful = models.BooleanField(default=False)
    failure_reason = models.TextField(blank=True)

    # Additional info
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        db_table = 'payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['booking', 'is_successful']),
            models.Index(fields=['payment_date', 'payment_method']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - ${self.amount}"

    def save(self, *args, **kwargs):
        # Auto-generate transaction ID
        if not self.transaction_id:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.transaction_id = f"TXN{timestamp}"

        super().save(*args, **kwargs)

        # Update booking paid amount
        if self.is_successful and self.payment_type != 'refund':
            self.booking.paid_amount += self.amount

            # Update payment status
            if self.booking.paid_amount >= self.booking.total_amount:
                self.booking.payment_status = 'paid'
            elif self.booking.paid_amount > 0:
                self.booking.payment_status = 'partial'

            self.booking.save()
