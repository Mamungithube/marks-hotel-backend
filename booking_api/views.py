# booking_api/views.py

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from django.utils import timezone

from .models import (
    RoomType, Room, RoomImage, Amenity, 
    RoomAmenity, Booking
)
from .serializers import (
    RoomTypeSerializer, RoomSerializer, RoomImageSerializer,
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

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'room', 'check_in_date', 'check_out_date']
    ordering_fields = ['booking_date', 'check_in_date', 'check_out_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        
        # Check if booking can be cancelled
        if booking.status != 'pending' and booking.status != 'confirmed':
            return Response(
                {"error": "Only pending or confirmed bookings can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if it's too late to cancel (e.g., within 24 hours of check-in)
        if booking.check_in_date <= timezone.now().date():
            return Response(
                {"error": "Cannot cancel a booking on or after the check-in date"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        return Response({"status": "Booking cancelled successfully"})


    permission_classes = [permissions.AllowAny]
    
