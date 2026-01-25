# # booking_api/views.py
# # ==========================================

# from rest_framework import viewsets, status, filters
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
# from django.utils import timezone
# from .models import Booking, Payment
# from .serializers import (
#     BookingListSerializer, BookingDetailSerializer,
#     BookingCreateSerializer, BookingUpdateSerializer,
#     BookingCancellationSerializer, PaymentSerializer
# )
# from royelhotel.permissions import IsOwnerOrAdmin


# class BookingViewSet(viewsets.ModelViewSet):
#     """
#     Booking CRUD
#     List: GET /api/bookings/
#     Create: POST /api/bookings/
#     Detail: GET /api/bookings/<id>/
#     """
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['booking_status', 'payment_status', 'check_in_date', 'check_out_date']
#     ordering_fields = ['created_at', 'check_in_date', 'check_out_date']
    
#     def get_queryset(self):
#         """Filter based on user role"""
#         user = self.request.user
        
#         if user.is_admin or user.is_finance:
#             return Booking.objects.all().select_related('user', 'room', 'room__room_type')
#         elif user.is_hotel_staff:
#             return Booking.objects.all().select_related('user', 'room', 'room__room_type')
#         else:
#             # Customers see only their bookings
#             return Booking.objects.filter(user=user).select_related('room', 'room__room_type')
    
#     def get_serializer_class(self):
#         if self.action == 'list':
#             return BookingListSerializer
#         elif self.action == 'create':
#             return BookingCreateSerializer
#         elif self.action in ['update', 'partial_update']:
#             return BookingUpdateSerializer
#         return BookingDetailSerializer
    
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
    
#     @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
#     def cancel(self, request, pk=None):
#         """
#         Cancel booking
#         POST /api/bookings/<id>/cancel/
#         Body: {"cancellation_reason": "Changed plans"}
#         """
#         booking = self.get_object()
#         serializer = BookingCancellationSerializer(
#             instance=booking,
#             data=request.data
#         )
#         serializer.is_valid(raise_exception=True)
        
#         # Update booking
#         booking.booking_status = 'cancelled'
#         booking.cancelled_at = timezone.now()
#         booking.cancelled_by = request.user
#         booking.cancellation_reason = serializer.validated_data['cancellation_reason']
#         booking.save()
        
#         # Update room status
#         booking.room.current_status = 'available'
#         booking.room.save()
        
#         return Response({
#             'message': 'Booking cancelled successfully',
#             'booking': BookingDetailSerializer(booking).data
#         })
    
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
#     def check_in(self, request, pk=None):
#         """
#         Check-in guest (Staff/Admin only)
#         POST /api/bookings/<id>/check_in/
#         """
#         if not (request.user.is_hotel_staff or request.user.is_admin):
#             return Response(
#                 {'error': 'Only staff can perform check-in'},
#                 status=status.HTTP_403_FORBIDDEN
#             )
        
#         booking = self.get_object()
        
#         if booking.booking_status != 'confirmed':
#             return Response(
#                 {'error': 'Only confirmed bookings can be checked in'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         booking.booking_status = 'checked_in'
#         booking.actual_check_in = timezone.now()
#         booking.save()
        
#         # Update room status
#         booking.room.current_status = 'occupied'
#         booking.room.save()
        
#         return Response({
#             'message': 'Check-in successful',
#             'booking': BookingDetailSerializer(booking).data
#         })
    
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
#     def check_out(self, request, pk=None):
#         """
#         Check-out guest (Staff/Admin only)
#         POST /api/bookings/<id>/check_out/
#         """
#         if not (request.user.is_hotel_staff or request.user.is_admin):
#             return Response(
#                 {'error': 'Only staff can perform check-out'},
#                 status=status.HTTP_403_FORBIDDEN
#             )
        
#         booking = self.get_object()
        
#         if booking.booking_status != 'checked_in':
#             return Response(
#                 {'error': 'Only checked-in bookings can be checked out'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         booking.booking_status = 'checked_out'
#         booking.actual_check_out = timezone.now()
#         booking.save()
        
#         # Update room status to cleaning
#         booking.room.current_status = 'cleaning'
#         booking.room.save()
        
#         return Response({
#             'message': 'Check-out successful',
#             'booking': BookingDetailSerializer(booking).data
#         })


# class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     Payment View (Read-only)
#     List: GET /api/bookings/payments/
#     Detail: GET /api/bookings/payments/<id>/
#     """
#     serializer_class = PaymentSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['payment_method', 'payment_type', 'is_successful']
#     ordering_fields = ['payment_date', 'amount']
    
#     def get_queryset(self):
#         user = self.request.user
        
#         if user.is_admin or user.is_finance:
#             return Payment.objects.all().select_related('booking', 'booking__user')
#         elif user.is_hotel_staff:
#             return Payment.objects.none()  # Staff can't see payments
#         else:
#             return Payment.objects.filter(booking__user=user).select_related('booking')