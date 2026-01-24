# employees/serializers.py
# ==========================================

from rest_framework import serializers
from .models import Department, Designation, Employee, Shift
from authontication.serializers import UserSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    """Department Serializer"""
    manager_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description',
            'manager', 'manager_name', 'employee_count',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_manager_name(self, obj):
        if obj.manager:
            return obj.manager.get_full_name()
        return None
    
    def get_employee_count(self, obj):
        return obj.employees.filter(is_active=True).count()


class DesignationSerializer(serializers.ModelSerializer):
    """Designation Serializer"""
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Designation
        fields = [
            'id', 'title', 'department', 'department_name',
            'description', 'level', 'employee_count',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_employee_count(self, obj):
        return obj.employees.filter(is_active=True).count()


class ShiftSerializer(serializers.ModelSerializer):
    """Shift Serializer"""
    
    class Meta:
        model = Shift
        fields = [
            'id', 'name', 'start_time', 'end_time',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Employee List Serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    employment_type_display = serializers.CharField(
        source='get_employment_type_display',
        read_only=True
    )
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'user_name', 'user_email',
            'department_name', 'designation_title',
            'employment_type', 'employment_type_display',
            'joining_date', 'basic_salary',
            'is_active', 'created_at'
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Employee Detail Serializer"""
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    designation = DesignationSerializer(read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'user', 'department', 'designation',
            'employment_type', 'joining_date', 'resignation_date',
            'basic_salary',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation',
            'national_id', 'passport_number', 'education',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'employee_id', 'created_at', 'updated_at']


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Employee Creation Serializer"""
    user_id = serializers.UUIDField(write_only=True)
    department_id = serializers.UUIDField(write_only=True)
    designation_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'user_id', 'department_id', 'designation_id',
            'employment_type', 'joining_date', 'basic_salary',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation',
            'national_id', 'passport_number', 'education'
        ]
    
    def validate_user_id(self, value):
        """Check if user exists and is STAFF type"""
        from authontication.models import User
        try:
            user = User.objects.get(id=value)
            if user.user_type != User.STAFF:
                raise serializers.ValidationError(
                    "Selected user must have STAFF role."
                )
            if hasattr(user, 'employee_profile'):
                raise serializers.ValidationError(
                    "This user already has an employee profile."
                )
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid user selected.")
        return value
    
    def create(self, validated_data):
        """Create employee"""
        from authontication.models import User
        user = User.objects.get(id=validated_data.pop('user_id'))
        department = Department.objects.get(id=validated_data.pop('department_id'))
        designation = Designation.objects.get(id=validated_data.pop('designation_id'))
        
        employee = Employee.objects.create(
            user=user,
            department=department,
            designation=designation,
            **validated_data
        )
        return employee