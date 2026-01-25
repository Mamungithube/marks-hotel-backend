# core/views.py or create dashboard app
# ==========================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from rest_framework import status
from django.db.models import F


class AdminDashboardView(APIView):
    """
    Admin Dashboard - Complete Overview
    GET /api/dashboard/admin/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access only'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from booking_api.models import Booking
        from room_management.models import Room
        from employees.models import Employee
        from review.models import Review
        
        today = timezone.now().date()
        
        # Booking stats
        total_bookings = Booking.objects.filter(is_active=True).count()
        today_bookings = Booking.objects.filter(created_at__date=today).count()
        pending_bookings = Booking.objects.filter(
            booking_status='pending',
            is_active=True
        ).count()
        
        # Room stats
        total_rooms = Room.objects.filter(is_active=True).count()
        available_rooms = Room.objects.filter(
            current_status='available',
            is_active=True
        ).count()
        occupied_rooms = Room.objects.filter(
            current_status='occupied',
            is_active=True
        ).count()
        
        # Employee stats
        total_employees = Employee.objects.filter(is_active=True).count()
        
        # Review stats
        total_reviews = Review.objects.filter(is_active=True).count()
        pending_reviews = Review.objects.filter(
            is_approved=False,
            is_active=True
        ).count()
        avg_rating = Review.objects.filter(
            is_approved=True
        ).aggregate(avg=Avg('overall_rating'))['avg'] or 0
        
        return Response({
            'bookings': {
                'total': total_bookings,
                'today': today_bookings,
                'pending': pending_bookings
            },
            'rooms': {
                'total': total_rooms,
                'available': available_rooms,
                'occupied': occupied_rooms,
                'occupancy_rate': round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 2)
            },
            'employees': {
                'total': total_employees
            },
            'reviews': {
                'total': total_reviews,
                'pending_approval': pending_reviews,
                'average_rating': round(avg_rating, 2)
            }
        })


class CustomerDashboardView(APIView):
    """
    Customer Dashboard
    GET /api/dashboard/customer/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from booking_api.models import Booking
        from review.models import Review
        
        user = request.user
        
        # Bookings
        total_bookings = Booking.objects.filter(user=user, is_active=True).count()
        upcoming_bookings = Booking.objects.filter(
            user=user,
            check_in_date__gte=timezone.now().date(),
            booking_status__in=['confirmed', 'pending'],
            is_active=True
        ).count()
        completed_bookings = Booking.objects.filter(
            user=user,
            booking_status='checked_out',
            is_active=True
        ).count()
        
        # Reviews
        total_reviews = Review.objects.filter(user=user, is_active=True).count()
        
        # Pending payments
        pending_amount = Booking.objects.filter(
            user=user,
            payment_status__in=['pending', 'partial'],
            is_active=True
        ).aggregate(
            total=Sum(F('total_amount') - F('paid_amount'))
        )['total'] or Decimal('0.00')
        
        return Response({
            'bookings': {
                'total': total_bookings,
                'upcoming': upcoming_bookings,
                'completed': completed_bookings
            },
            'reviews': {
                'total': total_reviews
            },
            'payments': {
                'pending_amount': pending_amount
            }
        })


class StaffDashboardView(APIView):
    """
    Staff Dashboard
    GET /api/dashboard/staff/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_hotel_staff:
            return Response(
                {'error': 'Staff access only'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from booking_api.models import Booking
        from housekeeping.models import HousekeepingTask
        
        today = timezone.now().date()
        
        # Today's check-ins/outs
        today_checkins = Booking.objects.filter(
            check_in_date=today,
            booking_status='confirmed',
            is_active=True
        ).count()
        
        today_checkouts = Booking.objects.filter(
            check_out_date=today,
            booking_status='checked_in',
            is_active=True
        ).count()
        
        # Current check-ins
        current_guests = Booking.objects.filter(
            booking_status='checked_in',
            is_active=True
        ).count()
        
        # Housekeeping tasks
        if hasattr(request.user, 'employee_profile'):
            my_tasks = HousekeepingTask.objects.filter(
                assigned_to__user=request.user,
                status__in=['pending', 'in_progress'],
                is_active=True
            ).count()
        else:
            my_tasks = 0
        
        pending_tasks = HousekeepingTask.objects.filter(
            status='pending',
            is_active=True
        ).count()
        
        return Response({
            'today': {
                'check_ins': today_checkins,
                'check_outs': today_checkouts,
                'current_guests': current_guests
            },
            'tasks': {
                'my_tasks': my_tasks,
                'pending_tasks': pending_tasks
            }
        })