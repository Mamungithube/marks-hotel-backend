from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
router = DefaultRouter()
router.register('review', views.ReviewViewset)
router.register('contect', views.ContactusViewset)
urlpatterns = [
    path('', include(router.urls)),
]