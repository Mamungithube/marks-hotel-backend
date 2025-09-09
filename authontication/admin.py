from django.contrib import admin
from .models import CustomUser, Customer

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'first_name', 'last_name', 'otp', 'is_verified']
    list_filter = ['is_verified']
    search_fields = ['user__username', 'email', 'first_name', 'last_name']
    readonly_fields = ['otp']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'image']
    search_fields = ['user__username', 'email']