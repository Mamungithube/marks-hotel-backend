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
#     User
# )


# # ==========================================
# # BASE ADMIN MIXINS FOR REUSABILITY
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


# class ReadOnlyAdminMixin:
#     """
#     Make admin read-only for certain user roles
#     """
#     def has_add_permission(self, request):
#         if request.user.is_customer:
#             return False
#         return super().has_add_permission(request)
    
#     def has_delete_permission(self, request, obj=None):
#         if request.user.is_customer or request.user.is_hotel_staff:
#             return False
#         return super().has_delete_permission(request, obj)


# # ==========================================
# # 1. USER MANAGEMENT ADMIN
# # ==========================================

# @admin.register(User)
# class CustomUserAdmin(BaseUserAdmin, ExportCsvMixin):
#     """
#     Custom User Admin with role-based display
#     """
#     list_display = [
#         'email', 'get_full_name', 'user_type_badge', 'is_verified_badge',
#         'is_active', 'last_login', 'created_at'
#     ]
#     list_filter = [
#         'user_type', 'is_verified', 'is_active', 'is_staff',
#         'is_superuser', 'created_at'
#     ]
#     search_fields = ['email', 'first_name', 'last_name', 'phone_number']
#     ordering = ['-created_at']
    
#     readonly_fields = [
#         'id', 'created_at', 'updated_at', 'last_login',
#         'email_verified_at', 'otp_created_at'
#     ]
    
#     fieldsets = (
#         (_('Authentication'), {
#             'fields': ('email', 'password')
#         }),
#         (_('Personal Info'), {
#             'fields': (
#                 'first_name', 'last_name', 'phone_number',
#                 'date_of_birth', 'profile_image'
#             )
#         }),
#         (_('Address'), {
#             'fields': ('address', 'city', 'country', 'postal_code'),
#             'classes': ('collapse',)
#         }),
#         (_('Role & Permissions'), {
#             'fields': (
#                 'user_type', 'is_verified', 'is_staff',
#                 'is_superuser', 'is_active', 'groups', 'user_permissions'
#             )
#         }),
#         (_('Verification'), {
#             'fields': ('otp', 'otp_created_at', 'email_verified_at'),
#             'classes': ('collapse',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'last_login', 'last_login_ip', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': (
#                 'email', 'password1', 'password2', 'first_name',
#                 'last_name', 'user_type', 'is_verified'
#             ),
#         }),
#     )
    
#     actions = ['export_as_csv', 'verify_users', 'activate_users', 'deactivate_users']
    
#     def user_type_badge(self, obj):
#         """Display user type with color badges"""
#         colors = {
#             'admin': 'red',
#             'customer': 'blue',
#             'staff': 'green',
#             'finance': 'purple'
#         }
#         color = colors.get(obj.user_type, 'gray')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 10px; '
#             'border-radius: 3px; font-weight: bold;">{}</span>',
#             color,
#             obj.get_user_type_display()
#         )
#     user_type_badge.short_description = 'Role'
    
#     def is_verified_badge(self, obj):
#         """Display verification status with icon"""
#         if obj.is_verified:
#             return format_html(
#                 '<span style="color: green;">✓ Verified</span>'
#             )
#         return format_html(
#             '<span style="color: red;">✗ Not Verified</span>'
#         )
#     is_verified_badge.short_description = 'Verified'
    
#     def verify_users(self, request, queryset):
#         """Bulk verify users"""
#         updated = queryset.update(
#             is_verified=True,
#             email_verified_at=timezone.now()
#         )
#         self.message_user(request, f'{updated} users verified successfully.')
#     verify_users.short_description = "Verify selected users"
    
#     def activate_users(self, request, queryset):
#         updated = queryset.update(is_active=True)
#         self.message_user(request, f'{updated} users activated.')
#     activate_users.short_description = "Activate selected users"
    
#     def deactivate_users(self, request, queryset):
#         updated = queryset.update(is_active=False)
#         self.message_user(request, f'{updated} users deactivated.')
#     deactivate_users.short_description = "Deactivate selected users"
    
#     def get_queryset(self, request):
#         """Role-based queryset filtering"""
#         qs = super().get_queryset(request)
        
#         # Customers can only see themselves
#         if request.user.is_customer:
#             return qs.filter(id=request.user.id)
        
#         # Staff can see customers only
#         if request.user.is_hotel_staff:
#             return qs.filter(user_type=User.CUSTOMER)
        
#         # Finance and Admin see all
#         return qs
