# room_management/models.py
# ==========================================

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, EmailValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from authontication.models import SoftDeleteModel

# ==========================================
# 3. ROOM MANAGEMENT MODELS
# ==========================================

class RoomType(SoftDeleteModel):
    """
    Room Type - Deluxe, Suite, Standard etc.
    """
    name = models.CharField(_('room type name'), max_length=100, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(_('description'))
    short_description = models.CharField(max_length=255, blank=True)
    
    # Pricing
    base_price = models.DecimalField(
        _('base price per night'),  
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    weekend_price = models.DecimalField(
        _('weekend price per night'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Capacity
    max_adults = models.PositiveIntegerField(default=2)
    max_children = models.PositiveIntegerField(default=2)
    max_occupancy = models.PositiveIntegerField(default=4)
    
    # Size and features
    size_sqm = models.PositiveIntegerField(
        _('size in square meters'),
        validators=[MinValueValidator(1)]
    )
    
    # Images
    primary_image = models.URLField(max_length=500, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    # Display order
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('room type')
        verbose_name_plural = _('room types')
        db_table = 'room_types'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['is_featured', 'display_order']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_price(self, date):
        """Get price based on date (weekend/weekday)"""
        if date.weekday() >= 5 and self.weekend_price:  # Saturday/Sunday
            return self.weekend_price
        return self.base_price


class RoomImage(SoftDeleteModel):
    """
    Multiple images for each room type
    """
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.URLField(max_length=500)
    caption = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('room image')
        verbose_name_plural = _('room images')
        db_table = 'room_images'
        ordering = ['room_type', 'display_order']
        indexes = [
            models.Index(fields=['room_type', 'is_primary']),
        ]
    
    def __str__(self):
        return f"Image for {self.room_type.name}"
    
    def save(self, *args, **kwargs):
        # If this is primary, remove primary from others
        if self.is_primary:
            RoomImage.objects.filter(
                room_type=self.room_type,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class Amenity(SoftDeleteModel):
    """
    Room amenities - WiFi, AC, TV etc.
    """
    CATEGORY_CHOICES = (
        ('basic', _('Basic')),
        ('entertainment', _('Entertainment')),
        ('comfort', _('Comfort')),
        ('safety', _('Safety')),
        ('bathroom', _('Bathroom')),
        ('other', _('Other')),
    )
    
    name = models.CharField(_('amenity name'), max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    icon = models.CharField(max_length=50, blank=True)  # Icon class or emoji
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _('amenity')
        verbose_name_plural = _('amenities')
        db_table = 'amenities'
        ordering = ['category', 'display_order', 'name']
    
    def __str__(self):
        return self.name


class RoomTypeAmenity(models.Model):
    """
    Many-to-many relationship between RoomType and Amenity
    """
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name='room_amenities'
    )
    amenity = models.ForeignKey(
        Amenity,
        on_delete=models.CASCADE,
        related_name='room_types'
    )
    is_complimentary = models.BooleanField(default=True)
    additional_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    class Meta:
        verbose_name = _('room type amenity')
        verbose_name_plural = _('room type amenities')
        db_table = 'room_type_amenities'
        unique_together = ('room_type', 'amenity')
    
    def __str__(self):
        return f"{self.room_type.name} - {self.amenity.name}"


class Room(SoftDeleteModel):
    """
    Individual rooms - প্রতিটা physical room
    """
    ROOM_STATUS_CHOICES = (
        ('available', _('Available')),
        ('occupied', _('Occupied')),
        ('cleaning', _('Cleaning')),
        ('maintenance', _('Under Maintenance')),
        ('reserved', _('Reserved')),
        ('out_of_order', _('Out of Order')),
    )
    
    room_number = models.CharField(
        _('room number'),
        max_length=10,
        unique=True,
        db_index=True
    )
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name='rooms'
    )
    
    # Location
    floor = models.PositiveIntegerField(
        _('floor number'),
        validators=[MinValueValidator(1)]
    )
    building = models.CharField(max_length=50, blank=True)
    
    # Features
    has_view = models.BooleanField(_('has view'), default=False)
    view_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("e.g., Sea View, City View, Garden View")
    )
    has_balcony = models.BooleanField(_('has balcony'), default=False)
    is_accessible = models.BooleanField(
        _('wheelchair accessible'),
        default=False
    )
    
    # Status
    current_status = models.CharField(
        max_length=20,
        choices=ROOM_STATUS_CHOICES,
        default='available',
        db_index=True
    )
    
    # Maintenance
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('room')
        verbose_name_plural = _('rooms')
        db_table = 'rooms'
        ordering = ['room_number']
        indexes = [
            models.Index(fields=['room_type', 'current_status', 'is_active']),
            models.Index(fields=['floor', 'building']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['room_number', 'is_active'],
                name='unique_active_room_number'
            )
        ]
    
    def __str__(self):
        return f"{self.room_number} - {self.room_type.name}"
    
    @property
    def is_available(self):
        """Check if room is available for booking"""
        return self.current_status == 'available' and self.is_active

