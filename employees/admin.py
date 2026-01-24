from django.contrib import admin
from .models import Employee, Department, Designation

admin.site.register(Department)
admin.site.register(Designation)
admin.site.register(Employee)
