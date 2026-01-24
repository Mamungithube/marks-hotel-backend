# housekeeping/serializers.py
# ==========================================

from rest_framework import serializers
from housekeeping.models import HousekeepingTask, MaintenanceRequest
from room_management.serializers import RoomSerializer
from employees.serializers import EmployeeListSerializer


class HousekeepingTaskSerializer(serializers.ModelSerializer):
    """Housekeeping Task Serializer"""
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    task_type_display = serializers.CharField(
        source='get_task_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = HousekeepingTask
        fields = [
            'id', 'room', 'room_number',
            'assigned_to', 'assigned_to_name',
            'task_type', 'task_type_display',
            'status', 'status_display',
            'scheduled_date', 'scheduled_time',
            'started_at', 'completed_at',
            'priority', 'notes', 'completion_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'started_at', 'completed_at',
            'created_at', 'updated_at'
        ]
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.user.get_full_name()
        return None


class HousekeepingTaskCreateSerializer(serializers.ModelSerializer):
    """Housekeeping Task Creation Serializer"""
    room_id = serializers.UUIDField(write_only=True)
    assigned_to_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = HousekeepingTask
        fields = [
            'room_id', 'assigned_to_id', 'task_type',
            'scheduled_date', 'scheduled_time',
            'priority', 'notes'
        ]


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """Maintenance Request Serializer"""
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    reported_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'room', 'room_number',
            'reported_by', 'reported_by_name',
            'assigned_to', 'assigned_to_name',
            'issue_type', 'description',
            'priority', 'priority_display',
            'status', 'status_display',
            'resolution_notes', 'resolved_at',
            'estimated_cost', 'actual_cost',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'reported_by', 'resolved_at',
            'created_at', 'updated_at'
        ]
    
    def get_reported_by_name(self, obj):
        if obj.reported_by:
            return obj.reported_by.get_full_name()
        return None
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.user.get_full_name()
        return None


class MaintenanceRequestCreateSerializer(serializers.ModelSerializer):
    """Maintenance Request Creation Serializer"""
    room_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'room_id', 'issue_type', 'description',
            'priority', 'estimated_cost'
        ]
    
    def create(self, validated_data):
        """Create maintenance request"""
        from room_management.models import Room
        room = Room.objects.get(id=validated_data.pop('room_id'))
        
        request_obj = MaintenanceRequest.objects.create(
            room=room,
            reported_by=self.context['request'].user,
            **validated_data
        )
        
        # Update room status to maintenance
        room.current_status = 'maintenance'
        room.save()
        
        return request_obj
