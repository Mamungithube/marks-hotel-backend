# # housekeeping/views.py
# # ==========================================

# from rest_framework import viewsets, filters
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
# from django.utils import timezone
# from housekeeping.models import HousekeepingTask, MaintenanceRequest
# from housekeeping.serializers import (
#     HousekeepingTaskSerializer, HousekeepingTaskCreateSerializer,
#     MaintenanceRequestSerializer, MaintenanceRequestCreateSerializer
# )
# from core.permissions import IsStaffUser, IsAdminUser


# class HousekeepingTaskViewSet(viewsets.ModelViewSet):
#     """Housekeeping Task CRUD (Staff/Admin)"""
#     permission_classes = [IsStaffUser]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['status', 'task_type', 'priority', 'scheduled_date']
#     ordering_fields = ['scheduled_date', 'priority', 'created_at']
    
#     def get_queryset(self):
#         user = self.request.user
#         queryset = HousekeepingTask.objects.filter(is_active=True).select_related(
#             'room', 'assigned_to', 'assigned_to__user'
#         )
        
#         # Staff see only their assigned tasks
#         if user.is_hotel_staff and not user.is_admin:
#             queryset = queryset.filter(assigned_to__user=user)
        
#         return queryset
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return HousekeepingTaskCreateSerializer
#         return HousekeepingTaskSerializer
    
#     @action(detail=True, methods=['post'])
#     def start(self, request, pk=None):
#         """Start task"""
#         task = self.get_object()
        
#         if task.status != 'pending':
#             return Response(
#                 {'error': 'Only pending tasks can be started'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         task.status = 'in_progress'
#         task.started_at = timezone.now()
#         task.save()
        
#         return Response({'message': 'Task started'})
    
#     @action(detail=True, methods=['post'])
#     def complete(self, request, pk=None):
#         """Complete task"""
#         task = self.get_object()
#         completion_notes = request.data.get('completion_notes', '')
        
#         if task.status not in ['pending', 'in_progress']:
#             return Response(
#                 {'error': 'Task already completed or cancelled'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         task.status = 'completed'
#         task.completed_at = timezone.now()
#         task.completion_notes = completion_notes
#         task.save()
        
#         # Update room status to available if it was cleaning
#         if task.room.current_status == 'cleaning':
#             task.room.current_status = 'available'
#             task.room.save()
        
#         return Response({'message': 'Task completed successfully'})
        

# class MaintenanceRequestViewSet(viewsets.ModelViewSet):
#     """Maintenance Request CRUD (Staff/Admin)"""
#     permission_classes = [IsStaffUser]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['status', 'priority', 'issue_type']
#     ordering_fields = ['created_at', 'priority']
    
#     def get_queryset(self):
#         return MaintenanceRequest.objects.filter(is_active=True).select_related(
#             'room', 'reported_by', 'assigned_to', 'assigned_to__user'
#         )
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return MaintenanceRequestCreateSerializer
#         return MaintenanceRequestSerializer
    
#     @action(detail=True, methods=['post'])
#     def assign(self, request, pk=None):
#         """Assign maintenance to employee"""
#         if not request.user.is_admin:
#             return Response(
#                 {'error': 'Only admin can assign maintenance'},
#                 status=status.HTTP_403_FORBIDDEN
#             )
        
#         maintenance = self.get_object()
#         employee_id = request.data.get('employee_id')
        
#         if not employee_id:
#             return Response(
#                 {'error': 'employee_id required'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         from employees.models import Employee
#         try:
#             employee = Employee.objects.get(id=employee_id, is_active=True)
#         except Employee.DoesNotExist:
#             return Response(
#                 {'error': 'Invalid employee'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         maintenance.assigned_to = employee
#         maintenance.status = 'assigned'
#         maintenance.save()
        
#         return Response({'message': 'Maintenance assigned successfully'})
    
#     @action(detail=True, methods=['post'])
#     def complete(self, request, pk=None):
#         """Complete maintenance"""
#         maintenance = self.get_object()
#         resolution_notes = request.data.get('resolution_notes', '')
#         actual_cost = request.data.get('actual_cost')
        
#         maintenance.status = 'completed'
#         maintenance.resolved_at = timezone.now()
#         maintenance.resolution_notes = resolution_notes
        
#         if actual_cost:
#             maintenance.actual_cost = actual_cost
        
#         maintenance.save()
        
#         # Update room status back to available
#         maintenance.room.current_status = 'available'
#         maintenance.room.save()
        
#         return Response({'message': 'Maintenance completed'})