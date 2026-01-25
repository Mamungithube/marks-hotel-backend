"""
URL configuration for royelhotel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import AdminDashboardView, CustomerDashboardView, StaffDashboardView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/',include('authontication.urls')),
    # path('gust/',include('review.urls')),
    # path('api/', include('booking_api.urls')),
    # path('employees_api/', include('employees.urls')),


    # deshboard urls
    
    path('api/v1/dashboard/admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('api/v1/dashboard/customer/', CustomerDashboardView.as_view(), name='customer-dashboard'),
    path('api/v1/dashboard/staff/', StaffDashboardView.as_view(), name='staff-dashboard'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)