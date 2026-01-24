# room_management/serializers.py
# ==========================================

from rest_framework import serializers
from .models import RoomType, RoomImage, Amenity, RoomTypeAmenity, Room


class AmenitySerializer(serializers.ModelSerializer):
    """Amenity Serializer"""
    
    class Meta:
        model = Amenity
        fields = [
            'id', 'name', 'category', 'icon',
            'description', 'display_order', 'is_active'
        ]
        read_only_fields = ['id']


class RoomImageSerializer(serializers.ModelSerializer):
    """Room Image Serializer"""
    
    class Meta:
        model = RoomImage
        fields = [
            'id', 'image_url', 'caption',
            'display_order', 'is_primary'
        ]
        read_only_fields = ['id']


class RoomTypeAmenitySerializer(serializers.ModelSerializer):
    """Room Type Amenity Serializer with amenity details"""
    amenity = AmenitySerializer(read_only=True)
    amenity_id = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.filter(is_active=True),
        source='amenity',
        write_only=True
    )
    
    class Meta:
        model = RoomTypeAmenity
        fields = [
            'id', 'amenity', 'amenity_id',
            'is_complimentary', 'additional_charge'
        ]


class RoomTypeListSerializer(serializers.ModelSerializer):
    """
    Room Type List Serializer - for list view
    """
    total_rooms = serializers.SerializerMethodField()
    available_rooms = serializers.SerializerMethodField()
    amenities_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'name', 'slug', 'short_description',
            'base_price', 'weekend_price', 'max_occupancy',
            'size_sqm', 'primary_image', 'is_featured',
            'total_rooms', 'available_rooms', 'amenities_count'
        ]
    
    def get_total_rooms(self, obj):
        return obj.rooms.filter(is_active=True).count()
    
    def get_available_rooms(self, obj):
        return obj.rooms.filter(
            is_active=True,
            current_status='available'
        ).count()
    
    def get_amenities_count(self, obj):
        return obj.room_amenities.count()


class RoomTypeDetailSerializer(serializers.ModelSerializer):
    """
    Room Type Detail Serializer - for detail view
    """
    images = RoomImageSerializer(many=True, read_only=True)
    amenities = RoomTypeAmenitySerializer(
        source='room_amenities',
        many=True,
        read_only=True
    )
    total_rooms = serializers.SerializerMethodField()
    available_rooms = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'base_price', 'weekend_price',
            'max_adults', 'max_children', 'max_occupancy',
            'size_sqm', 'primary_image',
            'images', 'amenities',
            'meta_title', 'meta_description',
            'display_order', 'is_featured', 'is_active',
            'total_rooms', 'available_rooms',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_rooms(self, obj):
        return obj.rooms.filter(is_active=True).count()
    
    def get_available_rooms(self, obj):
        return obj.rooms.filter(
            is_active=True,
            current_status='available'
        ).count()


class RoomTypeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Room Type Create/Update Serializer
    """
    amenity_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = RoomType
        fields = [
            'name', 'slug', 'description', 'short_description',
            'base_price', 'weekend_price',
            'max_adults', 'max_children', 'max_occupancy',
            'size_sqm', 'primary_image',
            'meta_title', 'meta_description',
            'display_order', 'is_featured',
            'amenity_ids'
        ]
    
    def create(self, validated_data):
        amenity_ids = validated_data.pop('amenity_ids', [])
        room_type = RoomType.objects.create(**validated_data)
        
        # Add amenities
        for amenity_id in amenity_ids:
            RoomTypeAmenity.objects.create(
                room_type=room_type,
                amenity_id=amenity_id
            )
        
        return room_type
    
    def update(self, instance, validated_data):
        amenity_ids = validated_data.pop('amenity_ids', None)
        
        # Update room type
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update amenities if provided
        if amenity_ids is not None:
            instance.room_amenities.all().delete()
            for amenity_id in amenity_ids:
                RoomTypeAmenity.objects.create(
                    room_type=instance,
                    amenity_id=amenity_id
                )
        
        return instance


class RoomSerializer(serializers.ModelSerializer):
    """
    Room Serializer with room type details
    """
    room_type_detail = RoomTypeListSerializer(source='room_type', read_only=True)
    room_type_id = serializers.PrimaryKeyRelatedField(
        queryset=RoomType.objects.filter(is_active=True),
        source='room_type',
        write_only=True
    )
    status_display = serializers.CharField(
        source='get_current_status_display',
        read_only=True
    )
    
    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'room_type', 'room_type_id',
            'room_type_detail', 'floor', 'building',
            'has_view', 'view_type', 'has_balcony', 'is_accessible',
            'current_status', 'status_display',
            'last_maintenance_date', 'next_maintenance_date',
            'maintenance_notes', 'is_active', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_available', 'created_at', 'updated_at']


class RoomListSerializer(serializers.ModelSerializer):
    """
    Simplified Room List Serializer
    """
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    status_display = serializers.CharField(
        source='get_current_status_display',
        read_only=True
    )
    
    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'room_type_name',
            'floor', 'current_status', 'status_display',
            'has_view', 'has_balcony', 'is_available'
        ]