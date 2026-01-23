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
from booking_api.models import Booking
from authontication.models import User
from room_management.models import Room
from employees.models import Employee

# ==========================================
# 6. REVIEW & FEEDBACK MODELS
# ==========================================

class Review(SoftDeleteModel):
    """
    Guest reviews and ratings
    """
    RATING_CHOICES = (
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    )
    
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    # Ratings
    overall_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    cleanliness_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    service_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    value_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Review text
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(_('review comment'))
    
    # Status
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Verified after booking completion")
    )
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reviews'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Helpful votes
    helpful_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        db_table = 'reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking', 'user']),
            models.Index(fields=['overall_rating', 'is_approved']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['booking', 'user'],
                name='one_review_per_booking'
            )
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.overall_rating}⭐"
    
    def save(self, *args, **kwargs):
        # Auto-verify if booking is completed
        if self.booking.booking_status == 'checked_out':
            self.is_verified = True
        super().save(*args, **kwargs)


class ContactMessage(SoftDeleteModel):
    """
    Contact us messages from guests
    """
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    STATUS_CHOICES = (
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    )
    
    # Contact info
    name = models.CharField(_('full name'), max_length=150)
    email = models.EmailField(_('email address'))
    phone = models.CharField(max_length=15, blank=True)
    
    # Message
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # For registered users
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_messages'
    )
    
    # Management
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        db_index=True
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_contacts'
    )
    
    # Response
    response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_responses'
    )
    
    class Meta:
        verbose_name = _('contact message')
        verbose_name_plural = _('contact messages')
        db_table = 'contact_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['email', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


# ==========================================
# 7. HOUSEKEEPING & MAINTENANCE MODELS
# ==========================================

class HousekeepingTask(SoftDeleteModel):
    """
    Room cleaning and housekeeping tasks
    """
    TASK_TYPE_CHOICES = (
        ('regular_cleaning', _('Regular Cleaning')),
        ('deep_cleaning', _('Deep Cleaning')),
        ('turndown_service', _('Turndown Service')),
        ('checkout_cleaning', _('Checkout Cleaning')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='housekeeping_tasks'
    )
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='housekeeping_tasks'
    )
    
    task_type = models.CharField(
        max_length=30,
        choices=TASK_TYPE_CHOICES,
        default='regular_cleaning'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    # Timing
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Details
    priority = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("1=Low, 5=High")
    )
    notes = models.TextField(blank=True)
    completion_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('housekeeping task')
        verbose_name_plural = _('housekeeping tasks')
        db_table = 'housekeeping_tasks'
        ordering = ['-scheduled_date', '-priority']
        indexes = [
            models.Index(fields=['room', 'status', 'scheduled_date']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.room.room_number} - {self.get_task_type_display()}"


class MaintenanceRequest(SoftDeleteModel):
    """
    Room maintenance and repair requests
    """
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    )
    
    STATUS_CHOICES = (
        ('reported', _('Reported')),
        ('assigned', _('Assigned')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_maintenance'
    )
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance'
    )
    
    # Issue details
    issue_type = models.CharField(
        max_length=100,
        help_text=_("e.g., Plumbing, Electrical, AC, etc.")
    )
    description = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='reported',
        db_index=True
    )
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    class Meta:
        verbose_name = _('maintenance request')
        verbose_name_plural = _('maintenance requests')
        db_table = 'maintenance_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['room', 'status']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.room.room_number} - {self.issue_type}"