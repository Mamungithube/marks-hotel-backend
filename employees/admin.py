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
# from .models import (HousekeepingTask, MaintenanceRequest,
# )

# # ==========================================
# # 6. HOUSEKEEPING & MAINTENANCE ADMIN
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
    

# @admin.register(HousekeepingTask)
# class HousekeepingTaskAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Housekeeping Task Admin"""
#     list_display = [
#         'id', 'room_link', 'task_type', 'assigned_to_link',
#         'status_badge', 'priority', 'scheduled_date', 'created_at'
#     ]
#     list_filter = [
#         'task_type', 'status', 'priority',
#         'scheduled_date', 'created_at'
#     ]
#     search_fields = ['room__room_number', 'notes']
#     date_hierarchy = 'scheduled_date'
    
#     readonly_fields = [
#         'id', 'created_at', 'updated_at',
#         'started_at', 'completed_at'
#     ]
    
#     autocomplete_fields = ['room', 'assigned_to']
    
#     fieldsets = (
#         (_('Task Information'), {
#             'fields': (
#                 'room', 'task_type', 'assigned_to',
#                 'scheduled_date', 'scheduled_time'
#             )
#         }),
#         (_('Details'), {
#             'fields': ('priority', 'status', 'notes')
#         }),
#         (_('Completion'), {
#             'fields': (
#                 'started_at', 'completed_at', 'completion_notes'
#             ),
#             'classes': ('collapse',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = [
#         'export_as_csv', 'mark_in_progress',
#         'mark_completed', 'mark_cancelled'
#     ]
    
#     def room_link(self, obj):
#         url = reverse('admin:yourapp_room_change', args=[obj.room.id])
#         return format_html('<a href="{}">{}</a>', url, obj.room.room_number)
#     room_link.short_description = 'Room'
    
#     def assigned_to_link(self, obj):
#         if obj.assigned_to:
#             url = reverse('admin:yourapp_employee_change', args=[obj.assigned_to.id])
#             return format_html(
#                 '<a href="{}">{}</a>',
#                 url,
#                 obj.assigned_to.user.get_full_name()
#             )
#         return '-'
#     assigned_to_link.short_description = 'Assigned To'
    
#     def status_badge(self, obj):
#         colors = {
#             'pending': '#ffc107',
#             'in_progress': '#17a2b8',
#             'completed': '#28a745',
#             'cancelled': '#6c757d'
#         }
#         color = colors.get(obj.status, '#6c757d')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 8px; '
#             'border-radius: 3px;">{}</span>',
#             color,
#             obj.get_status_display()
#         )
#     status_badge.short_description = 'Status'
    
#     def mark_in_progress(self, request, queryset):
#         updated = queryset.filter(status='pending').update(
#             status='in_progress',
#             started_at=timezone.now()
#         )
#         self.message_user(request, f'{updated} tasks marked as in progress.')
#     mark_in_progress.short_description = "Mark as In Progress"
    
#     def mark_completed(self, request, queryset):
#         updated = queryset.exclude(status='completed').update(
#             status='completed',
#             completed_at=timezone.now()
#         )
#         self.message_user(request, f'{updated} tasks marked as completed.')
#     mark_completed.short_description = "Mark as Completed"
    
#     def mark_cancelled(self, request, queryset):
#         updated = queryset.exclude(
#             status__in=['completed', 'cancelled']
#         ).update(status='cancelled')
#         self.message_user(request, f'{updated} tasks cancelled.')
#     mark_cancelled.short_description = "Cancel Tasks"


