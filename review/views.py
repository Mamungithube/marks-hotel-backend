# # review/views.py
# # ==========================================

# from rest_framework import viewsets, status, filters
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
# from django_filters.rest_framework import DjangoFilterBackend
# from .models import Review, ContactMessage
# from .serializers import (
#     ReviewSerializer, ReviewCreateSerializer,
#     ContactMessageSerializer, ContactMessageCreateSerializer
# )
# from core.permissions import IsOwnerOrAdmin, IsAdminUser


# class ReviewViewSet(viewsets.ModelViewSet):
#     """Review CRUD"""
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['overall_rating', 'is_approved', 'is_verified']
#     ordering_fields = ['created_at', 'overall_rating', 'helpful_count']
    
#     def get_queryset(self):
#         """Only approved reviews for public, all for admin"""
#         if self.request.user.is_authenticated and self.request.user.is_admin:
#             return Review.objects.all().select_related('user', 'booking')
#         return Review.objects.filter(is_approved=True, is_active=True).select_related('user', 'booking')
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return ReviewCreateSerializer
#         return ReviewSerializer
    
#     def get_permissions(self):
#         if self.action == 'create':
#             return [IsAuthenticated()]
#         elif self.action in ['update', 'partial_update', 'destroy']:
#             return [IsOwnerOrAdmin()]
#         return [IsAuthenticatedOrReadOnly()]
    
#     @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
#     def approve(self, request, pk=None):
#         """Approve review (Admin only)"""
#         review = self.get_object()
#         review.is_approved = True
#         review.approved_by = request.user
#         review.approved_at = timezone.now()
#         review.save()
        
#         return Response({'message': 'Review approved'})
    
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
#     def mark_helpful(self, request, pk=None):
#         """Mark review as helpful"""
#         review = self.get_object()
#         review.helpful_count += 1
#         review.save()
        
#         return Response({'helpful_count': review.helpful_count})


# class ContactMessageViewSet(viewsets.ModelViewSet):
#     """Contact Message CRUD"""
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['status', 'priority']
#     ordering_fields = ['created_at', 'priority']
    
#     def get_queryset(self):
#         user = self.request.user
        
#         if user.is_authenticated and (user.is_admin or user.is_hotel_staff):
#             return ContactMessage.objects.all()
#         elif user.is_authenticated:
#             return ContactMessage.objects.filter(user=user)
#         return ContactMessage.objects.none()
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return ContactMessageCreateSerializer
#         return ContactMessageSerializer
    
#     def get_permissions(self):
#         if self.action == 'create':
#             return [permissions.AllowAny()]
#         return [IsAuthenticated()]
    
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
#     def respond(self, request, pk=None):
#         """Respond to contact message (Staff/Admin)"""
#         if not (request.user.is_hotel_staff or request.user.is_admin):
#             return Response(
#                 {'error': 'Only staff can respond'},
#                 status=status.HTTP_403_FORBIDDEN
#             )
        
#         message = self.get_object()
#         response_text = request.data.get('response')
        
#         if not response_text:
#             return Response(
#                 {'error': 'Response text required'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         message.response = response_text
#         message.responded_at = timezone.now()
#         message.responded_by = request.user
#         message.status = 'resolved'
#         message.save()
        
#         return Response({'message': 'Response sent successfully'})
