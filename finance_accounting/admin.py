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

# # Import all models
# from .models import (
#     Invoice, InvoiceItem, Expense, Revenue, FinancialReport
# )

# # ==========================================
# # 7. FINANCE MODULE ADMIN (Finance Team Access)
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


# class InvoiceItemInline(admin.TabularInline):
#     """Inline for invoice items"""
#     model = InvoiceItem
#     extra = 1
#     fields = ['description', 'quantity', 'unit_price', 'amount']
#     readonly_fields = ['amount']


# @admin.register(Invoice)
# class InvoiceAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Invoice Admin - Finance Team"""
#     list_display = [
#         'invoice_number', 'booking_link',
#         'issue_date', 'due_date', 'status_badge',
#         'total_amount_display', 'balance_due_display'
#     ]
#     list_filter = ['status', 'issue_date', 'due_date', 'created_at']
#     search_fields = [
#         'invoice_number', 'booking__booking_number',
#         'booking__user__email'
#     ]
#     date_hierarchy = 'issue_date'
    
#     readonly_fields = [
#         'id', 'invoice_number', 'created_at', 'updated_at',
#         'total_amount', 'balance_due_display'
#     ]
    
#     autocomplete_fields = ['booking', 'created_by']
    
#     inlines = [InvoiceItemInline]
    
#     fieldsets = (
#         (_('Invoice Information'), {
#             'fields': ('invoice_number', 'booking', 'created_by')
#         }),
#         (_('Dates'), {
#             'fields': ('issue_date', 'due_date')
#         }),
#         (_('Amounts'), {
#             'fields': (
#                 'subtotal', 'tax_amount', 'discount_amount',
#                 'total_amount', 'paid_amount', 'balance_due_display'
#             )
#         }),
#         (_('Status'), {
#             'fields': ('status',)
#         }),
#         (_('Additional'), {
#             'fields': ('notes', 'terms_and_conditions', 'pdf_url'),
#             'classes': ('collapse',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = ['export_as_csv', 'mark_as_sent', 'mark_as_paid']
    
#     def booking_link(self, obj):
#         url = reverse('admin:yourapp_booking_change', args=[obj.booking.id])
#         return format_html('<a href="{}">{}</a>', url, obj.booking.booking_number)
#     booking_link.short_description = 'Booking'
    
#     def status_badge(self, obj):
#         colors = {
#             'draft': '#6c757d',
#             'sent': '#17a2b8',
#             'paid': '#28a745',
#             'partially_paid': '#ffc107',
#             'overdue': '#dc3545',
#             'cancelled': '#343a40'
#         }
#         color = colors.get(obj.status, '#6c757d')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 8px; '
#             'border-radius: 3px;">{}</span>',
#             color,
#             obj.get_status_display()
#         )
#     status_badge.short_description = 'Status'
    
#     def total_amount_display(self, obj):
#         return format_html(
#             '<span style="font-weight: bold;">${}</span>',
#             obj.total_amount
#         )
#     total_amount_display.short_description = 'Total'
    
#     def balance_due_display(self, obj):
#         balance = obj.balance_due
#         if balance > 0:
#             return format_html(
#                 '<span style="color: red; font-weight: bold;">${}</span>',
#                 balance
#             )
#         return format_html('<span style="color: green;">$0.00</span>')
#     balance_due_display.short_description = 'Balance Due'
    
#     def mark_as_sent(self, request, queryset):
#         updated = queryset.filter(status='draft').update(status='sent')
#         self.message_user(request, f'{updated} invoices marked as sent.')
#     mark_as_sent.short_description = "Mark as Sent"
    
#     def mark_as_paid(self, request, queryset):
#         updated = queryset.exclude(status='paid').update(status='paid')
#         self.message_user(request, f'{updated} invoices marked as paid.')
#     mark_as_paid.short_description = "Mark as Paid"
    
#     def get_queryset(self, request):
#         """Only Finance and Admin can see invoices"""
#         qs = super().get_queryset(request)
        
#         if request.user.is_customer:
#             return qs.filter(booking__user=request.user)
        
#         if request.user.is_hotel_staff:
#             return qs.none()
        
#         return qs
    
#     def has_module_permission(self, request):
#         """Only Finance and Admin have access"""
#         return request.user.is_finance or request.user.is_admin


# @admin.register(Expense)
# class ExpenseAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Expense Admin - Finance Team Only"""
#     list_display = [
#         'expense_number', 'category', 'vendor_name',
#         'amount_display', 'expense_date',
#         'payment_status_badge', 'approval_badge', 'recorded_by'
#     ]
#     list_filter = [
#         'category', 'payment_status', 'is_approved',
#         'expense_date', 'created_at'
#     ]
#     search_fields = [
#         'expense_number', 'description',
#         'vendor_name', 'related_employee__employee_id'
#     ]
#     date_hierarchy = 'expense_date'
    
#     readonly_fields = [
#         'id', 'expense_number', 'created_at', 'updated_at'
#     ]
    
#     autocomplete_fields = [
#         'related_employee', 'related_maintenance',
#         'recorded_by', 'approved_by'
#     ]
    
#     fieldsets = (
#         (_('Expense Information'), {
#             'fields': (
#                 'expense_number', 'category', 'description', 'amount'
#             )
#         }),
#         (_('Dates'), {
#             'fields': ('expense_date', 'payment_date')
#         }),
#         (_('Vendor'), {
#             'fields': ('vendor_name',)
#         }),
#         (_('Related Records'), {
#             'fields': ('related_employee', 'related_maintenance'),
#             'classes': ('collapse',)
#         }),
#         (_('Status'), {
#             'fields': ('payment_status', 'is_approved', 'approved_by')
#         }),
#         (_('Documents'), {
#             'fields': ('receipt_url',),
#             'classes': ('collapse',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'recorded_by', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = ['export_as_csv', 'approve_expenses', 'mark_as_paid']
    
#     def amount_display(self, obj):
#         return format_html(
#             '<span style="color: red; font-weight: bold;">${}</span>',
#             obj.amount
#         )
#     amount_display.short_description = 'Amount'
#     amount_display.admin_order_field = 'amount'
    
#     def payment_status_badge(self, obj):
#         colors = {
#             'pending': '#ffc107',
#             'paid': '#28a745',
#             'partial': '#fd7e14'
#         }
#         color = colors.get(obj.payment_status, '#6c757d')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 8px; '
#             'border-radius: 3px;">{}</span>',
#             color,
#             obj.get_payment_status_display()
#         )
#     payment_status_badge.short_description = 'Payment'
    
#     def approval_badge(self, obj):
#         if obj.is_approved:
#             return format_html(
#                 '<span style="color: green; font-weight: bold;">✓ Approved</span>'
#             )
#         return format_html(
#             '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
#         )
#     approval_badge.short_description = 'Approval'
    
#     def approve_expenses(self, request, queryset):
#         updated = queryset.update(
#             is_approved=True,
#             approved_by=request.user
#         )
#         self.message_user(request, f'{updated} expenses approved.')
#     approve_expenses.short_description = "Approve selected expenses"
    
#     def mark_as_paid(self, request, queryset):
#         updated = queryset.update(
#             payment_status='paid',
#             payment_date=timezone.now().date()
#         )
#         self.message_user(request, f'{updated} expenses marked as paid.')
#     mark_as_paid.short_description = "Mark as Paid"
    
#     def save_model(self, request, obj, form, change):
#         if not obj.recorded_by:
#             obj.recorded_by = request.user
#         super().save_model(request, obj, form, change)
    
#     def has_module_permission(self, request):
#         """Only Finance and Admin"""
#         return request.user.is_finance or request.user.is_admin


# @admin.register(Revenue)
# class RevenueAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Revenue Admin - Finance Dashboard"""
#     list_display = [
#         'revenue_number', 'source', 'amount_display',
#         'revenue_date', 'booking_link', 'created_at'
#     ]
#     list_filter = ['source', 'revenue_date', 'created_at']
#     search_fields = [
#         'revenue_number', 'description',
#         'related_booking__booking_number'
#     ]
#     date_hierarchy = 'revenue_date'
    
#     readonly_fields = [
#         'id', 'revenue_number', 'created_at', 'updated_at'
#     ]
    
#     autocomplete_fields = ['related_booking', 'related_payment']
    
#     fieldsets = (
#         (_('Revenue Information'), {
#             'fields': (
#                 'revenue_number', 'source',
#                 'description', 'amount', 'revenue_date'
#             )
#         }),
#         (_('Related Records'), {
#             'fields': ('related_booking', 'related_payment'),
#             'classes': ('collapse',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = ['export_as_csv']
    
#     def amount_display(self, obj):
#         return format_html(
#             '<span style="color: green; font-weight: bold;">${}</span>',
#             obj.amount
#         )
#     amount_display.short_description = 'Amount'
#     amount_display.admin_order_field = 'amount'
    
#     def booking_link(self, obj):
#         if obj.related_booking:
#             url = reverse('admin:yourapp_booking_change', args=[obj.related_booking.id])
#             return format_html('<a href="{}">{}</a>', url, obj.related_booking.booking_number)
#         return '-'
#     booking_link.short_description = 'Booking'
    
#     def has_module_permission(self, request):
#         """Only Finance and Admin"""
#         return request.user.is_finance or request.user.is_admin


# @admin.register(FinancialReport)
# class FinancialReportAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Financial Report Admin - Finance Dashboard"""
#     list_display = [
#         'report_type', 'report_date',
#         'revenue_display', 'expense_display',
#         'profit_display', 'occupancy_display', 'generated_by'
#     ]
#     list_filter = ['report_type', 'report_date', 'created_at']
#     search_fields = ['report_type']
#     date_hierarchy = 'report_date'
    
#     readonly_fields = [
#         'id', 'created_at', 'updated_at',
#         'net_profit', 'occupancy_rate'
#     ]
    
#     autocomplete_fields = ['generated_by']
    
#     fieldsets = (
#         (_('Report Information'), {
#             'fields': (
#                 'report_type', 'report_date',
#                 'start_date', 'end_date', 'generated_by'
#             )
#         }),
#         (_('Financial Summary'), {
#             'fields': (
#                 'total_revenue', 'total_expenses', 'net_profit'
#             )
#         }),
#         (_('Booking Statistics'), { 
#             'fields': (
#                 'total_bookings', 'total_guests',
#                 'average_daily_rate', 'occupancy_rate'
#             )
#         }),
#     )
    
#     def user_link(self, obj):
#         url = reverse('admin:yourapp_user_change', args=[obj.user.id])
#         return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
#     user_link.short_description = 'Guest'
    
#     def room_link(self, obj):
#         url = reverse('admin:yourapp_room_change', args=[obj.room.id])
#         return format_html('<a href="{}">{}</a>', url, obj.room.room_number)
#     room_link.short_description = 'Room'
    
#     def nights(self, obj):
#         return obj.number_of_nights
#     nights.short_description = 'Nights'
    
#     def booking_status_badge(self, obj):
#         colors = {
#             'pending': '#ffc107',
#             'confirmed': '#28a745',
#             'checked_in': '#17a2b8',
#             'checked_out': '#6c757d',
#             'cancelled': '#dc3545',
#             'no_show': '#343a40'
#         }
#         color = colors.get(obj.booking_status, '#6c757d')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 10px; '
#             'border-radius: 3px;">{}</span>',
#             color,
#             obj.get_booking_status_display()
#         )
#     booking_status_badge.short_description = 'Booking Status'
    
#     def payment_status_badge(self, obj):
#         colors = {
#             'pending': '#ffc107',
#             'partial': '#fd7e14',
#             'paid': '#28a745',
#             'refunded': '#6c757d',
#             'failed': '#dc3545'
#         }
#         color = colors.get(obj.payment_status, '#6c757d')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 10px; '
#             'border-radius: 3px;">{}</span>',
#             color,
#             obj.get_payment_status_display()
#         )
#     payment_status_badge.short_description = 'Payment Status'
    
#     def total_amount_display(self, obj):
#         return f"${obj.total_amount}"
#     total_amount_display.short_description = 'Total'
#     total_amount_display.admin_order_field = 'total_amount'
    
#     def balance_amount_display(self, obj):
#         balance = obj.balance_amount
#         if balance > 0:
#             return format_html(
#                 '<span style="color: red; font-weight: bold;">${}</span>',
#                 balance
#             )
#         return format_html('<span style="color: green;">$0.00</span>')
#     balance_amount_display.short_description = 'Balance Due'
    
#     # Bulk actions
#     def confirm_bookings(self, request, queryset):
#         updated = queryset.filter(
#             booking_status='pending'
#         ).update(booking_status='confirmed')
#         self.message_user(request, f'{updated} bookings confirmed.')
#     confirm_bookings.short_description = "Confirm selected bookings"
    
#     def cancel_bookings(self, request, queryset):
#         updated = queryset.exclude(
#             booking_status__in=['checked_out', 'cancelled']
#         ).update(
#             booking_status='cancelled',
#             cancelled_at=timezone.now(),
#             cancelled_by=request.user
#         )
#         self.message_user(request, f'{updated} bookings cancelled.')
#     cancel_bookings.short_description = "Cancel selected bookings"
    
#     def mark_as_checked_in(self, request, queryset):
#         updated = queryset.filter(
#             booking_status='confirmed'
#         ).update(
#             booking_status='checked_in',
#             actual_check_in=timezone.now()
#         )
#         self.message_user(request, f'{updated} bookings checked in.')
#     mark_as_checked_in.short_description = "Mark as Checked In"
    
#     def mark_as_checked_out(self, request, queryset):
#         updated = queryset.filter(
#             booking_status='checked_in'
#         ).update(
#             booking_status='checked_out',
#             actual_check_out=timezone.now()
#         )
#         self.message_user(request, f'{updated} bookings checked out.')
#     mark_as_checked_out.short_description = "Mark as Checked Out"
    
#     def get_queryset(self, request):
#         """Role-based filtering"""
#         qs = super().get_queryset(request)
        
#         # Customers see only their bookings
#         if request.user.is_customer:
#             return qs.filter(user=request.user)
        
#         # All others see all bookings
#         return qs


# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Payment Transaction Admin"""
#     list_display = [
#         'transaction_id', 'booking_link', 'amount_display',
#         'payment_method', 'payment_type', 'success_badge', 'payment_date'
#     ]
#     list_filter = [
#         'payment_method', 'payment_type',
#         'is_successful', 'payment_date'
#     ]
#     search_fields = [
#         'transaction_id', 'booking__booking_number',
#         'stripe_payment_intent_id', 'stripe_charge_id'
#     ]
#     date_hierarchy = 'payment_date'
    
#     readonly_fields = [
#         'id', 'transaction_id', 'payment_date', 'created_at', 'updated_at'
#     ]
    
#     autocomplete_fields = ['booking']
    
#     fieldsets = (
#         (_('Payment Information'), {
#             'fields': (
#                 'transaction_id', 'booking', 'amount',
#                 'payment_method', 'payment_type'
#             )
#         }),
#         (_('Status'), {
#             'fields': ('is_successful', 'failure_reason')
#         }),
#         (_('Stripe Details'), {
#             'fields': ('stripe_payment_intent_id', 'stripe_charge_id'),
#             'classes': ('collapse',)
#         }),
#         (_('Additional'), {
#             'fields': ('notes', 'payment_date'),
#             'classes': ('collapse',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = ['export_as_csv']
    
#     def booking_link(self, obj):
#         url = reverse('admin:yourapp_booking_change', args=[obj.booking.id])
#         return format_html('<a href="{}">{}</a>', url, obj.booking.booking_number)
#     booking_link.short_description = 'Booking'
    
#     def amount_display(self, obj):
#         return format_html(
#             '<span style="font-weight: bold; color: green;">${}</span>',
#             obj.amount
#         )
#     amount_display.short_description = 'Amount'
#     amount_display.admin_order_field = 'amount'
    
#     def success_badge(self, obj):
#         if obj.is_successful:
#             return format_html(
#                 '<span style="color: green; font-weight: bold;">✓ Success</span>'
#             )
#         return format_html(
#             '<span style="color: red; font-weight: bold;">✗ Failed</span>'
#         )
#     success_badge.short_description = 'Status'
    
#     def get_queryset(self, request):
#         """Role-based filtering"""
#         qs = super().get_queryset(request)
        
#         # Customers see only their payments
#         if request.user.is_customer:
#             return qs.filter(booking__user=request.user)
        
#         # Staff cannot see payments
#         if request.user.is_hotel_staff:
#             return qs.none()
        
#         # Finance and Admin see all
#         return qs
    
#     def has_add_permission(self, request):
#         # Only Finance and Admin can add payments manually
#         return request.user.is_finance or request.user.is_admin
    
#     def has_delete_permission(self, request, obj=None):
#         # Only Admin can delete payments
#         return request.user.is_admin