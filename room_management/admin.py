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
#     RoomType, RoomImage, Amenity, RoomTypeAmenity, Room
# )


# # ==========================================
# # 2. ROOM MANAGEMENT ADMIN
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


# class RoomImageInline(admin.TabularInline):
#     """Inline for room images"""
#     model = RoomImage
#     extra = 1
#     fields = ['image_url', 'caption', 'is_primary', 'display_order']
#     classes = ['collapse']


# class RoomTypeAmenityInline(admin.TabularInline):
#     """Inline for room amenities"""
#     model = RoomTypeAmenity
#     extra = 1
#     autocomplete_fields = ['amenity']
#     fields = ['amenity', 'is_complimentary', 'additional_charge']


# @admin.register(RoomType)
# class RoomTypeAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Room Type Admin"""
#     list_display = [
#         'name', 'base_price_display', 'weekend_price_display',
#         'max_occupancy', 'size_sqm', 'room_count', 'is_featured', 'is_active'
#     ]
#     list_filter = ['is_featured', 'is_active', 'created_at']
#     search_fields = ['name', 'description', 'slug']
#     prepopulated_fields = {'slug': ('name',)}
    
#     readonly_fields = ['id', 'created_at', 'updated_at']
    
#     fieldsets = (
#         (_('Basic Information'), {
#             'fields': ('name', 'slug', 'description', 'short_description')
#         }),
#         (_('Pricing'), {
#             'fields': ('base_price', 'weekend_price')
#         }),
#         (_('Capacity'), {
#             'fields': ('max_adults', 'max_children', 'max_occupancy')
#         }),
#         (_('Details'), {
#             'fields': ('size_sqm', 'primary_image')
#         }),
#         (_('Display Settings'), {
#             'fields': ('is_featured', 'display_order', 'is_active')
#         }),
#         (_('SEO'), {
#             'fields': ('meta_title', 'meta_description'),
#             'classes': ('collapse',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     inlines = [RoomImageInline, RoomTypeAmenityInline]
#     actions = ['export_as_csv', 'feature_rooms', 'unfeature_rooms']
    
#     def base_price_display(self, obj):
#         return f"${obj.base_price}"
#     base_price_display.short_description = 'Base Price'
#     base_price_display.admin_order_field = 'base_price'
    
#     def weekend_price_display(self, obj):
#         if obj.weekend_price:
#             return f"${obj.weekend_price}"
#         return "-"
#     weekend_price_display.short_description = 'Weekend Price'
    
#     def room_count(self, obj):
#         """Show number of rooms of this type"""
#         count = obj.rooms.filter(is_active=True).count()
#         url = reverse('admin:yourapp_room_changelist') + f'?room_type__id__exact={obj.id}'
#         return format_html('<a href="{}">{} rooms</a>', url, count)
#     room_count.short_description = 'Total Rooms'
    
#     def feature_rooms(self, request, queryset):
#         updated = queryset.update(is_featured=True)
#         self.message_user(request, f'{updated} room types featured.')
#     feature_rooms.short_description = "Feature selected room types"
    
#     def unfeature_rooms(self, request, queryset):
#         updated = queryset.update(is_featured=False)
#         self.message_user(request, f'{updated} room types unfeatured.')
#     unfeature_rooms.short_description = "Unfeature selected room types"


# @admin.register(Amenity)
# class AmenityAdmin(admin.ModelAdmin):
#     """Amenity Admin"""
#     list_display = ['name', 'category', 'icon', 'display_order', 'is_active']
#     list_filter = ['category', 'is_active']
#     search_fields = ['name', 'description']
    
#     fieldsets = (
#         (None, {
#             'fields': ('name', 'category', 'icon', 'description', 'display_order')
#         }),
#         (_('Status'), {
#             'fields': ('is_active',)
#         }),
#     )


# @admin.register(Room)
# class RoomAdmin(admin.ModelAdmin, ExportCsvMixin):
#     """Individual Room Admin"""
#     list_display = [
#         'room_number', 'room_type', 'floor', 'status_badge',
#         'has_view_badge', 'has_balcony', 'is_active'
#     ]
#     list_filter = [
#         'room_type', 'current_status', 'floor',
#         'has_view', 'has_balcony', 'is_accessible', 'is_active'
#     ]
#     search_fields = ['room_number', 'view_type', 'building']
#     autocomplete_fields = ['room_type']
    
#     readonly_fields = ['id', 'created_at', 'updated_at']
    
#     fieldsets = (
#         (_('Basic Information'), {
#             'fields': ('room_number', 'room_type', 'current_status')
#         }),
#         (_('Location'), {
#             'fields': ('floor', 'building')
#         }),
#         (_('Features'), {
#             'fields': (
#                 'has_view', 'view_type', 'has_balcony', 'is_accessible'
#             )
#         }),
#         (_('Maintenance'), {
#             'fields': (
#                 'last_maintenance_date', 'next_maintenance_date',
#                 'maintenance_notes'
#             ),
#             'classes': ('collapse',)
#         }),
#         (_('Status'), {
#             'fields': ('is_active',)
#         }),
#         (_('Tracking'), {
#             'fields': ('id', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     actions = [
#         'export_as_csv', 'mark_as_available', 'mark_as_cleaning',
#         'mark_as_maintenance', 'mark_as_occupied'
#     ]
    
#     def status_badge(self, obj):
#         """Display status with color"""
#         colors = {
#             'available': '#28a745',
#             'occupied': '#dc3545',
#             'cleaning': '#ffc107',
#             'maintenance': '#fd7e14',
#             'reserved': '#17a2b8',
#             'out_of_order': '#6c757d'
#         }
#         color = colors.get(obj.current_status, '#6c757d')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 10px; '
#             'border-radius: 3px;">{}</span>',
#             color,
#             obj.get_current_status_display()
#         )
#     status_badge.short_description = 'Status'
    
#     def has_view_badge(self, obj):
#         if obj.has_view:
#             return format_html(
#                 '<span style="color: green;">✓ {}</span>',
#                 obj.view_type or 'Yes'
#             )
#         return format_html('<span style="color: gray;">-</span>')
#     has_view_badge.short_description = 'View'
    
#     # Bulk actions for status
#     def mark_as_available(self, request, queryset):
#         updated = queryset.update(current_status='available')
#         self.message_user(request, f'{updated} rooms marked as available.')
#     mark_as_available.short_description = "Mark as Available"
    
#     def mark_as_cleaning(self, request, queryset):
#         updated = queryset.update(current_status='cleaning')
#         self.message_user(request, f'{updated} rooms marked as cleaning.')
#     mark_as_cleaning.short_description = "Mark as Cleaning"
    
#     def mark_as_maintenance(self, request, queryset):
#         updated = queryset.update(current_status='maintenance')
#         self.message_user(request, f'{updated} rooms marked as maintenance.')
#     mark_as_maintenance.short_description = "Mark as Maintenance"
    
#     def mark_as_occupied(self, request, queryset):
#         updated = queryset.update(current_status='occupied')
#         self.message_user(request, f'{updated} rooms marked as occupied.')
#     mark_as_occupied.short_description = "Mark as Occupied"