from django.contrib import admin

# Register your models here.
from .models import HousekeepingTask,MaintenanceRequest

admin.site.register(HousekeepingTask)
admin.site.register(MaintenanceRequest)