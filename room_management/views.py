# room_management/views.py
# ==========================================

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from .models import RoomType, Room, Amenity, RoomImage
from .serializers import (
    RoomTypeListSerializer, RoomTypeDetailSerializer,
    RoomTypeCreateUpdateSerializer, RoomSerializer,
    RoomListSerializer, AmenitySerializer, RoomImageSerializer
)
from royelhotel.permissions import IsAdminOrReadOnly


class RoomTypeViewSet(viewsets.ModelViewSet):
    """
    RoomType CRUD
    List: GET /api/rooms/types/
    Detail: GET /api/rooms/types/<id>/
    Create: POST /api/rooms/types/
    Update: PUT/PATCH /api/rooms/types/<id>/
    Delete: DELETE /api/rooms/types/<id>/
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured', 'max_occupancy']
    search_fields = ['name', 'description']
    ordering_fields = ['base_price', 'name', 'display_order']
    
    def get_queryset(self):
        return RoomType.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RoomTypeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RoomTypeCreateUpdateSerializer
        return RoomTypeDetailSerializer
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Check room type availability
        GET /api/rooms/types/<id>/availability/?check_in=2025-01-25&check_out=2025-01-27
        """
        room_type = self.get_object()
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        if not check_in or not check_out:
            return Response(
                {'error': 'check_in and check_out dates required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from booking_api.models import Booking
        
        # Find booked rooms
        booked_rooms = Booking.objects.filter(
            room__room_type=room_type,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            booking_status__in=['pending', 'confirmed', 'checked_in'],
            is_active=True
        ).values_list('room__id', flat=True)
        
        # Available rooms
        available_rooms = Room.objects.filter(
            room_type=room_type,
            is_active=True
        ).exclude(id__in=booked_rooms)
        
        return Response({
            'room_type': room_type.name,
            'available_count': available_rooms.count(),
            'available_rooms': RoomListSerializer(available_rooms, many=True).data
        })


class RoomViewSet(viewsets.ModelViewSet):
    """
    Room CRUD
    List: GET /api/rooms/
    Detail: GET /api/rooms/<id>/
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_type', 'current_status', 'floor', 'has_view', 'has_balcony']
    search_fields = ['room_number']
    ordering_fields = ['room_number', 'floor']
    
    def get_queryset(self):
        return Room.objects.filter(is_active=True).select_related('room_type')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RoomListSerializer
        return RoomSerializer
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update room status
        POST /api/rooms/<id>/update_status/
        Body: {"status": "available"}
        """
        room = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Room.ROOM_STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room.current_status = new_status
        room.save()
        
        return Response({
            'message': 'Room status updated',
            'room': RoomSerializer(room).data
        })


class AmenityViewSet(viewsets.ModelViewSet):
    """Amenity CRUD"""
    serializer_class = AmenitySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Amenity.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']


class RoomImageViewSet(viewsets.ModelViewSet):
    """Room Image CRUD"""
    serializer_class = RoomImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = RoomImage.objects.filter(is_active=True)