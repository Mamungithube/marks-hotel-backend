from django.contrib import admin
from . import models
from .models import ContactUs
# Register your models here.
admin.site.register(models.Review)

class ContactModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'problem']
admin.site.register(ContactUs, ContactModelAdmin)