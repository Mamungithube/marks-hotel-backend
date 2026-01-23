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

# from authontication.admin import ExportCsvMixin

# # Import all models
# from .models import (
#     Review, ContactMessage
# )


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

# # ==========================================
# # 5. REVIEW & CONTACT ADMIN
# # ==========================================

# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Review Admin with approval workflow"""
#     list_display = [
#         'id', 'user_link', 'booking_link', 'rating_display',
#         'is_verified_badge', 'is_approved_badge',
#         'created_at'
#     ]
#     list_filter = [
#         'overall_rating', 'is_verified', 'is_approved',
#         'created_at'
#     ]
#     search_fields = [
#         'user__email', 'user__first_name',
#         'title', 'comment'
#     ]
#     date_hierarchy = 'created_at'
    
#     readonly_fields = [
#         'id', 'created_at', 'updated_at',
#         'approved_by', 'approved_at'
#     ]
    
#     autocomplete_fields = ['user', 'booking', 'approved_by']
    
#     fieldsets = (
#         (_('Review Information'), {
#             'fields': ('user', 'booking', 'title', 'comment')
#         }),
#         (_('Ratings'), {
#             'fields': (
#                 'overall_rating', 'cleanliness_rating',
#                 'service_rating', 'value_rating'
#             )
#         }),
#         (_('Status'), {
#             'fields': (
#                 'is_verified', 'is_approved',
#                 'approved_by', 'approved_at'
#             )
#         }),
#         (_('Engagement'), {
#             'fields': ('helpful_count',)
#         }),
#         (_('System'), {
#             'fields': ('is_active',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = ['export_as_csv', 'approve_reviews', 'reject_reviews']
    
#     def user_link(self, obj):
#         url = reverse('admin:yourapp_user_change', args=[obj.user.id])
#         return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
#     user_link.short_description = 'Reviewer'
    
#     def booking_link(self, obj):
#         url = reverse('admin:yourapp_booking_change', args=[obj.booking.id])
#         return format_html('<a href="{}">{}</a>', url, obj.booking.booking_number)
#     booking_link.short_description = 'Booking'
    
#     def rating_display(self, obj):
#         stars = '⭐' * obj.overall_rating
#         return format_html(
#             '<span style="font-size: 16px;">{}</span>',
#             stars
#         )
#     rating_display.short_description = 'Rating'
    
#     def is_verified_badge(self, obj):
#         if obj.is_verified:
#             return format_html('<span style="color: green;">✓</span>')
#         return format_html('<span style="color: gray;">-</span>')
#     is_verified_badge.short_description = 'Verified'
    
#     def is_approved_badge(self, obj):
#         if obj.is_approved:
#             return format_html(
#                 '<span style="color: green; font-weight: bold;">✓ Approved</span>'
#             )
#         return format_html(
#             '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
#         )
#     is_approved_badge.short_description = 'Status'
    
#     def approve_reviews(self, request, queryset):
#         updated = queryset.update(
#             is_approved=True,
#             approved_by=request.user,
#             approved_at=timezone.now()
#         )
#         self.message_user(request, f'{updated} reviews approved.')
#     approve_reviews.short_description = "Approve selected reviews"
    
#     def reject_reviews(self, request, queryset):
#         updated = queryset.update(
#             is_approved=False,
#             is_active=False
#         )
#         self.message_user(request, f'{updated} reviews rejected.')
#     reject_reviews.short_description = "Reject selected reviews"


# @admin.register(ContactMessage)
# class ContactMessageAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Contact Message Admin"""
#     list_display = [
#         'id', 'name', 'email', 'subject',
#         'priority_badge', 'status_badge',
#         'assigned_to', 'created_at'
#     ]
#     list_filter = ['priority', 'status', 'created_at']
#     search_fields = ['name', 'email', 'subject', 'message']
#     date_hierarchy = 'created_at'
    
#     readonly_fields = [
#         'id', 'created_at', 'updated_at',
#         'responded_at', 'responded_by'
#     ]
    
#     autocomplete_fields = ['user', 'assigned_to', 'responded_by']
    
#     fieldsets = (
#         (_('Contact Information'), {
#             'fields': ('name', 'email', 'phone', 'user')
#         }),
#         (_('Message'), {
#             'fields': ('subject', 'message')
#         }),
#         (_('Management'), {
#             'fields': ('priority', 'status', 'assigned_to')
#         }),
#         (_('Response'), {
#             'fields': ('response', 'responded_at', 'responded_by'),
#             'classes': ('collapse',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = ['export_as_csv', 'mark_as_resolved', 'assign_to_me']
    
#     def priority_badge(self, obj):
#         colors = {
#             'low': '#28a745',
#             'medium': '#ffc107',
#             'high': '#fd7e14',
#             'urgent': '#dc3545'
#         }
#         color = colors.get(obj.priority, '#6c757d')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 8px; '
#             'border-radius: 3px; text-transform: uppercase; font-size: 11px;">{}</span>',
#             color,
#             obj.get_priority_display()
#         )
#     priority_badge.short_description = 'Priority'
    
#     def status_badge(self, obj):
#         colors = {
#             'new': '#17a2b8',
#             'in_progress': '#ffc107',
#             'resolved': '#28a745',
#             'closed': '#6c757d'
#         }
#         color = colors.get(obj.status, '#6c757d')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 8px; '
#             'border-radius: 3px;">{}</span>',
#             color,
#             obj.get_status_display()
#         )
#     status_badge.short_description = 'Status'
    
#     def mark_as_resolved(self, request, queryset):
#         updated = queryset.update(status='resolved')
#         self.message_user(request, f'{updated} messages marked as resolved.')
#     mark_as_resolved.short_description = "Mark as Resolved"
    
#     def assign_to_me(self, request, queryset):
#         updated = queryset.update(
#             assigned_to=request.user,
#             status='in_progress'
#         )
#         self.message_user(request, f'{updated} messages assigned to you.')
#     assign_to_me.short_description = "Assign to Me"