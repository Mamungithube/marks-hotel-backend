# booking_api/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    capacity = models.PositiveIntegerField(default=2)
    size = models.PositiveIntegerField(help_text=_("Size in square meters"))
    floor = models.PositiveIntegerField(default=1)
    has_view = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['room_number']
    
    def __str__(self):
        return f"{self.room_number} - {self.room_type.name}"

# class RoomImage(models.Model):
#     room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='images')
#     is_primary = models.BooleanField(default=False)
    
#     def __str__(self):
#         return f"Image for {self.room_type.name}"

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
   
    class Meta:
        verbose_name_plural = "Amenities"
    
    def __str__(self):
        return self.name

class RoomAmenity(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='amenities')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Room Amenities"
        unique_together = ('room_type', 'amenity')
    
    def __str__(self):
        return f"{self.room_type.name} - {self.amenity.name}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)

    # Stripe fields
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.room.room_number}"

