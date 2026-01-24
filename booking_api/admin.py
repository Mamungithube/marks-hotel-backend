from django.contrib import admin
from django.db import models


from .models import Booking,Payment

admin.site.register(Booking)
admin.site.register(Payment)

