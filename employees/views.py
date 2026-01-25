# # employees/views.py
# # ==========================================

# from rest_framework import viewsets, filters
# from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
# from .models import Department, Designation, Employee, Shift
# from .serializers import (
#     DepartmentSerializer, DesignationSerializer,
#     EmployeeListSerializer, EmployeeDetailSerializer,
#     EmployeeCreateSerializer, ShiftSerializer
# )
# from core.permissions import IsAdminUser


# class DepartmentViewSet(viewsets.ModelViewSet):
#     """Department CRUD (Admin Only)"""
#     serializer_class = DepartmentSerializer
#     permission_classes = [IsAdminUser]
#     queryset = Department.objects.filter(is_active=True)
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['name', 'code']


# class DesignationViewSet(viewsets.ModelViewSet):
#     """Designation CRUD (Admin Only)"""
#     serializer_class = DesignationSerializer
#     permission_classes = [IsAdminUser]
#     queryset = Designation.objects.filter(is_active=True)
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     filterset_fields = ['department', 'level']
#     search_fields = ['title']


# class EmployeeViewSet(viewsets.ModelViewSet):
#     """Employee CRUD (Admin Only)"""
#     permission_classes = [IsAdminUser]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['department', 'designation', 'employment_type']
#     search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email']
#     ordering_fields = ['joining_date', 'basic_salary']
    
#     def get_queryset(self):
#         return Employee.objects.filter(is_active=True).select_related(
#             'user', 'department', 'designation'
#         )
    
#     def get_serializer_class(self):
#         if self.action == 'list':
#             return EmployeeListSerializer
#         elif self.action == 'create':
#             return EmployeeCreateSerializer
#         return EmployeeDetailSerializer


# class ShiftViewSet(viewsets.ModelViewSet):
#     """Shift CRUD (Admin Only)"""
#     serializer_class = ShiftSerializer
#     permission_classes = [IsAdminUser]
#     queryset = Shift.objects.filter(is_active=True)