# # notification/views.py
# # ==========================================

# from rest_framework import viewsets, status, filters
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from django_filters.rest_framework import DjangoFilterBackend
# from django.utils import timezone
# from notification.models import Notification, PromoCode, SiteSettings
# from notification.serializers import (
#     NotificationSerializer, PromoCodeSerializer,
#     PromoCodeValidationSerializer, SiteSettingsSerializer
# )
# from core.permissions import IsAdminUser


# class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
#     """User Notifications (Read-only)"""
#     serializer_class = NotificationSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['notification_type', 'is_read']
#     ordering_fields = ['created_at']
    
#     def get_queryset(self):
#         return Notification.objects.filter(
#             user=self.request.user,
#             is_active=True
#         ).select_related('related_booking')
    
#     @action(detail=True, methods=['post'])
#     def mark_read(self, request, pk=None):
#         """Mark notification as read"""
#         notification = self.get_object()
#         notification.mark_as_read()
        
#         return Response({'message': 'Marked as read'})
    
#     @action(detail=False, methods=['post'])
#     def mark_all_read(self, request):
#         """Mark all notifications as read"""
#         updated = self.get_queryset().filter(is_read=False).update(
#             is_read=True,
#             read_at=timezone.now()
#         )
        
#         return Response({'message': f'{updated} notifications marked as read'})
    
#     @action(detail=False, methods=['get'])
#     def unread_count(self, request):
#         """Get unread notification count"""
#         count = self.get_queryset().filter(is_read=False).count()
#         return Response({'unread_count': count})


# class PromoCodeViewSet(viewsets.ModelViewSet):
#     """Promo Code CRUD (Admin Only for create/update)"""
#     serializer_class = PromoCodeSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     filterset_fields = ['discount_type', 'is_active']
#     search_fields = ['code', 'description']
    
#     def get_queryset(self):
#         return PromoCode.objects.filter(is_active=True)
    
#     def get_permissions(self):
#         if self.action in ['list', 'retrieve', 'validate']:
#             return [IsAuthenticated()]
#         return [IsAdminUser()]
    
#     @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
#     def validate_code(self, request):
#         """
#         Validate promo code
#         POST /api/notifications/promo-codes/validate_code/
#         Body: {"code": "SAVE20", "booking_amount": 1000}
#         """
#         serializer = PromoCodeValidationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         promo = serializer.validated_data['promo']
#         discount = serializer.validated_data['discount_amount']
        
#         return Response({
#             'valid': True,
#             'promo_code': PromoCodeSerializer(promo).data,
#             'discount_amount': discount,
#             'message': f'Promo code applied! You save ${discount}'
#         })


# class SiteSettingsViewSet(viewsets.ModelViewSet):
#     """Site Settings (Admin for edit, All for read)"""
#     serializer_class = SiteSettingsSerializer
    
#     def get_queryset(self):
#         return SiteSettings.objects.all()
    
#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             return [AllowAny()]
#         return [IsAdminUser()]
    
#     def list(self, request):
#         """Get site settings"""
#         settings = SiteSettings.get_settings()
#         serializer = self.get_serializer(settings)
#         return Response(serializer.data)