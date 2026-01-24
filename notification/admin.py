from django.contrib import admin

# Register your models here.
from .models import Notification,PromoCode,SiteSettings

admin.site.register(Notification)
admin.site.register(PromoCode)
admin.site.register(SiteSettings)
