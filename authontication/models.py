# ==========================================
# COMPLETE PROFESSIONAL HOTEL MANAGEMENT MODELS
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


# ==========================================
# 1. BASE ABSTRACT MODELS
# ==========================================

class TimeStampedModel(models.Model):
    """
    Abstract base model - সব models এই class inherit করবে
    Automatic created_at, updated_at tracking
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteManager(models.Manager):
    """
    Custom manager for soft delete - deleted items hide করবে
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeleteModel(TimeStampedModel):
    """
    Soft delete pattern - data actually delete হবে না
    """
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = SoftDeleteManager()  # Default manager (only active items)
    all_objects = models.Manager()  # All items including deleted
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Override delete to perform soft delete"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self):
        """Actual database delete"""
        super().delete()
    
    def restore(self):
        """Restore soft deleted item"""
        self.is_active = True
        self.deleted_at = None
        self.save()


# ==========================================2. CUSTOM USER MODEL ==========================================

class CustomUserManager(BaseUserManager):
    """ Custom user manager - email দিয়ে login করবে """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email address is required'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom User Model - Email দিয়ে authentication
    4 Types of Users:
    1. ADMIN - Full system access
    2. CUSTOMER - Guest/Customer who books rooms
    3. STAFF - Hotel employees (housekeeping, reception, etc.)
    4. FINANCE - Finance department (accounts, billing, reports)
    
    """
    
    # Role Constants - এগুলো code এ use করবেন
    ADMIN = 'admin'
    CUSTOMER = 'customer'
    STAFF = 'staff'
    FINANCE = 'finance'
    
    USER_TYPE_CHOICES = (
        (ADMIN, _('Admin')),
        (CUSTOMER, _('Customer')),
        (STAFF, _('Staff')),
        (FINANCE, _('Finance')),
    )
    
    email = models.EmailField(
        _('email address'), 
        unique=True,
        validators=[EmailValidator()],
        db_index=True
    )
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    phone_number = models.CharField(
        _('phone number'),
        max_length=15,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        )]
    )
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default=CUSTOMER,  # Default হবে Customer
        db_index=True
    )
    
    # Profile fields
    profile_image = models.URLField(max_length=500, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # OTP fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['user_type', 'is_verified']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_otp_valid(self):
        """Check if OTP is still valid (10 minutes)"""
        if not self.otp or not self.otp_created_at:
            return False
        expiry_time = self.otp_created_at + timedelta(minutes=10)
        return timezone.now() < expiry_time
    
    # Role checking helper methods
    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.user_type == self.ADMIN or self.is_superuser
    
    @property
    def is_customer(self):
        """Check if user is customer"""
        return self.user_type == self.CUSTOMER
    
    @property
    def is_hotel_staff(self):
        """Check if user is hotel staff"""
        return self.user_type == self.STAFF
    
    @property
    def is_finance(self):
        """Check if user is finance team"""
        return self.user_type == self.FINANCE
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.user_type == role or self.is_superuser
