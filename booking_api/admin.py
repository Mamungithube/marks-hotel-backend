# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.utils.html import format_html
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as _
# from django.db.models import Sum, Count, Q
# from django.utils import timezone
# from datetime import timedelta
# import csv
# from django.http import HttpResponse
# from room_management.models import Room
# from .models import Booking
# from employees.models import Shift
# # ==========================================
# # 3. BOOKING MANAGEMENT ADMIN
# # ==========================================

# class ExportCsvMixin:
#     """
#     Mixin to add CSV export functionality to any admin
#     """
#     def export_as_csv(self, request, queryset):
#         meta = self.model._meta
#         field_names = [field.name for field in meta.fields]
        
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = f'attachment; filename={meta}.csv'
#         writer = csv.writer(response)
        
#         writer.writerow(field_names)
#         for obj in queryset:
#             writer.writerow([getattr(obj, field) for field in field_names])
        
#         return response
    
#     export_as_csv.short_description = "Export Selected as CSV"


# @admin.register(Booking)
# class BookingAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Booking Admin with comprehensive features"""
#     list_display = [
#         'booking_number', 'user_link', 'room_link',
#         'check_in_date', 'check_out_date', 'nights',
#         'booking_status_badge', 'payment_status_badge',
#         'total_amount_display', 'created_at'
#     ]
#     list_filter = [
#         'booking_status', 'payment_status',
#         'check_in_date', 'check_out_date', 'created_at'
#     ]
#     search_fields = [
#         'booking_number', 'user__email',
#         'user__first_name', 'user__last_name',
#         'room__room_number'
#     ]
#     date_hierarchy = 'check_in_date'
    
#     readonly_fields = [
#         'id', 'booking_number', 'created_at', 'updated_at',
#         'actual_check_in', 'actual_check_out', 'cancelled_at',
#         'nights', 'balance_amount_display'
#     ]
    
#     autocomplete_fields = ['user', 'room', 'cancelled_by']
    
#     fieldsets = (
#         (_('Booking Information'), {
#             'fields': ('booking_number', 'user', 'room')
#         }),
#         (_('Dates'), {
#             'fields': (
#                 'check_in_date', 'check_out_date',
#                 'actual_check_in', 'actual_check_out', 'nights'
#             )
#         }),
#         (_('Guests'), {
#             'fields': ('adults', 'children')
#         }),
#         (_('Status'), {
#             'fields': ('booking_status', 'payment_status')
#         }),
#         (_('Pricing'), {
#             'fields': (
#                 'base_amount', 'tax_amount', 'discount_amount',
#                 'total_amount', 'paid_amount', 'balance_amount_display'
#             )
#         }),
#         (_('Payment Integration'), {
#             'fields': ('stripe_payment_intent_id', 'stripe_customer_id'),
#             'classes': ('collapse',)
#         }),
#         (_('Requests & Notes'), {
#             'fields': ('special_requests', 'internal_notes'),
#             'classes': ('collapse',)
#         }),
#         (_('Cancellation'), {
#             'fields': (
#                 'cancelled_at', 'cancelled_by',
#                 'cancellation_reason', 'refund_amount'
#             ),
#             'classes': ('collapse',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = [
#         'export_as_csv', 'confirm_bookings', 'cancel_bookings',
#         'mark_as_checked_in', 'mark_as_checked_out'
#     ]
    
#     def user_link(self, obj):
#         url = reverse('admin:yourapp_user_change', args=[obj.user.id])
#         return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
#     user_link.short_description = 'Employee Name'
    
#     def salary_display(self, obj):
#         return format_html(
#             '<span style="color: green;">${}</span>',
#             obj.basic_salary
#         )
#     salary_display.short_description = 'Salary'
#     salary_display.admin_order_field = 'basic_salary'
    
#     def get_queryset(self, request):
#         """Only Admin and Finance can see employee data"""
#         qs = super().get_queryset(request)
        
#         if request.user.is_customer or request.user.is_hotel_staff:
#             return qs.filter(user=request.user)
        
#         return qs


# @admin.register(Shift)
# class ShiftAdmin(admin.ModelAdmin):
#     """Shift Admin"""
#     list_display = ['name', 'start_time', 'end_time', 'is_active']
#     list_filter = ['is_active']
#     search_fields = ['name']