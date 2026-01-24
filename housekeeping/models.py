# authenticate /models.py
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
from room_management.models import Room
from employees.models import Employee
from authontication.models import User

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

