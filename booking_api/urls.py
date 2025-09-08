# booking_api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoomTypeViewSet, RoomViewSet, AmenityViewSet,
    BookingViewSet ,stripe_webhook
)

router = DefaultRouter()
router.register(r'room-types', RoomTypeViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'amenities', AmenityViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
]