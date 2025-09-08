# booking_api/views.py

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from django.utils import timezone

from .models import (
    RoomType, Room, Amenity, 
    RoomAmenity, Booking
)
from .serializers import (
    RoomTypeSerializer, RoomSerializer,
    AmenitySerializer, BookingSerializer, UserSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly

class RoomTypeViewSet(viewsets.ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['price_per_night']
    search_fields = ['name', 'description']
    ordering_fields = ['price_per_night', 'name']
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Check availability of a room type for given dates"""
        room_type = self.get_object()
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        if not check_in or not check_out:
            return Response(
                {"error": "Please provide check_in and check_out dates"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if check_in_date >= check_out_date:
            return Response(
                {"error": "Check-out date must be after check-in date"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find rooms of this type that are not booked in the given date range
        booked_rooms = Booking.objects.filter(
            room__room_type=room_type,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            status__in=['pending', 'confirmed']
        ).values_list('room__id', flat=True)
        
        available_rooms = Room.objects.filter(room_type=room_type).exclude(id__in=booked_rooms)
        
        return Response({
            "room_type": room_type.name,
            "available_rooms_count": available_rooms.count(),
            "available_rooms": RoomSerializer(available_rooms, many=True).data
        })

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_type', 'capacity', 'floor', 'has_view', 'has_balcony']
    search_fields = ['room_number']
    ordering_fields = ['room_number', 'floor']
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        room = self.get_object()
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        if not check_in or not check_out:
            return Response(
                {"error": "Please provide check_in and check_out dates"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if check_in_date >= check_out_date:
            return Response(
                {"error": "Check-out date must be after check-in date"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if room is available for the requested dates
        conflicting_bookings = Booking.objects.filter(
            room=room,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            status__in=['pending', 'confirmed']
        )
        
        is_available = not conflicting_bookings.exists()
        
        return Response({
            "room": room.room_number,
            "is_available": is_available,
            "conflicting_bookings_count": conflicting_bookings.count() if not is_available else 0
        })

class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets, permissions, status, filters
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
import stripe
from django.conf import settings

from .models import Booking, Room
from .serializers import BookingSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'room', 'check_in_date', 'check_out_date']
    ordering_fields = ['booking_date', 'check_in_date', 'check_out_date']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Booking.objects.none()
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        """
        যখন বুকিং তৈরি হবে:
        1. total_price হিসাব করা হবে room_type.price_per_night থেকে
        2. Stripe PaymentIntent তৈরি করা হবে
        3. booking.payment_status = 'pending' থাকবে
        """
        booking = serializer.save(user=self.request.user)

        room = booking.room
        nights = (booking.check_out_date - booking.check_in_date).days or 1
        total_price = room.room_type.price_per_night * nights

        # Stripe PaymentIntent তৈরি
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # সেন্টে কনভার্ট
            currency="usd",
            metadata={"booking_id": booking.id, "user_id": self.request.user.id}
        )

        # booking আপডেট
        booking.payment_status = "pending"
        booking.stripe_payment_intent = intent.id
        booking.save()

        # ফ্রন্টএন্ডকে client_secret পাঠানো
        self.client_secret = intent.client_secret

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        # client_secret যোগ করা হচ্ছে response এ
        if hasattr(self, "client_secret"):
            response.data["client_secret"] = self.client_secret
        return response

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status not in ['pending', 'confirmed']:
            return Response(
                {"error": "Only pending or confirmed bookings can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.check_in_date <= timezone.now().date():
            return Response(
                {"error": "Cannot cancel a booking on or after the check-in date"},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.save()

        return Response({"status": "Booking cancelled successfully"})



from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = "your-webhook-secret"

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        booking = Booking.objects.filter(stripe_payment_intent=intent['id']).first()
        if booking:
            booking.payment_status = "paid"
            booking.save()

    return HttpResponse(status=200)