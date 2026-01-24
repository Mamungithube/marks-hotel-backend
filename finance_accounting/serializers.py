# finance_accounting/serializers.py
# ==========================================

from rest_framework import serializers
from finance_accounting.models import (
    Invoice, InvoiceItem, Expense, Revenue, FinancialReport
)
from booking_api.serializers import BookingListSerializer
from decimal import Decimal
from django.db import models
class InvoiceItemSerializer(serializers.ModelSerializer):
    """Invoice Item Serializer"""
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'description', 'quantity',
            'unit_price', 'amount'
        ]
        read_only_fields = ['id', 'amount']


class InvoiceSerializer(serializers.ModelSerializer):
    """Invoice Serializer"""
    booking_number = serializers.CharField(
        source='booking.booking_number',
        read_only=True
    )
    customer_name = serializers.CharField(
        source='booking.user.get_full_name',
        read_only=True
    )
    items = InvoiceItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    balance = serializers.DecimalField(
        source='balance_due',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    is_overdue_status = serializers.BooleanField(
        source='is_overdue',
        read_only=True
    )
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'booking', 'booking_number',
            'customer_name', 'issue_date', 'due_date',
            'subtotal', 'tax_amount', 'discount_amount',
            'total_amount', 'paid_amount', 'balance',
            'status', 'status_display',
            'notes', 'terms_and_conditions', 'pdf_url',
            'items', 'created_by', 'created_by_name',
            'is_overdue_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'total_amount',
            'created_at', 'updated_at'
        ]
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name()
        return None


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Invoice Creation Serializer"""
    booking_id = serializers.UUIDField(write_only=True)
    items = InvoiceItemSerializer(many=True)
    
    class Meta:
        model = Invoice
        fields = [
            'booking_id', 'due_date', 'subtotal',
            'tax_amount', 'discount_amount',
            'notes', 'terms_and_conditions', 'items'
        ]
    
    def create(self, validated_data):
        """Create invoice with items"""
        from booking_api.models import Booking
        items_data = validated_data.pop('items')
        booking = Booking.objects.get(id=validated_data.pop('booking_id'))
        
        invoice = Invoice.objects.create(
            booking=booking,
            created_by=self.context['request'].user,
            **validated_data
        )
        
        # Create invoice items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        return invoice


class ExpenseSerializer(serializers.ModelSerializer):
    """Expense Serializer"""
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )
    recorded_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    related_employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = [
            'id', 'expense_number', 'category', 'category_display',
            'description', 'amount',
            'expense_date', 'payment_date',
            'payment_status', 'payment_status_display',
            'vendor_name',
            'related_employee', 'related_employee_name',
            'related_maintenance',
            'receipt_url',
            'recorded_by', 'recorded_by_name',
            'approved_by', 'approved_by_name',
            'is_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'expense_number', 'recorded_by',
            'created_at', 'updated_at'
        ]
    
    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return obj.recorded_by.get_full_name()
        return None
    
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name()
        return None
    
    def get_related_employee_name(self, obj):
        if obj.related_employee:
            return obj.related_employee.user.get_full_name()
        return None


class ExpenseCreateSerializer(serializers.ModelSerializer):
    """Expense Creation Serializer"""
    related_employee_id = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True
    )
    related_maintenance_id = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Expense
        fields = [
            'category', 'description', 'amount',
            'expense_date', 'payment_date', 'payment_status',
            'vendor_name',
            'related_employee_id', 'related_maintenance_id',
            'receipt_url'
        ]
    
    def create(self, validated_data):
        """Create expense"""
        from employees.models import Employee
        from housekeeping.models import MaintenanceRequest
        
        related_employee_id = validated_data.pop('related_employee_id', None)
        related_maintenance_id = validated_data.pop('related_maintenance_id', None)
        
        expense = Expense.objects.create(
            recorded_by=self.context['request'].user,
            **validated_data
        )
        
        # Link related records
        if related_employee_id:
            expense.related_employee = Employee.objects.get(id=related_employee_id)
        if related_maintenance_id:
            expense.related_maintenance = MaintenanceRequest.objects.get(
                id=related_maintenance_id
            )
        
        expense.save()
        return expense


class RevenueSerializer(serializers.ModelSerializer):
    """Revenue Serializer"""
    source_display = serializers.CharField(
        source='get_source_display',
        read_only=True
    )
    booking_number = serializers.SerializerMethodField()
    
    class Meta:
        model = Revenue
        fields = [
            'id', 'revenue_number', 'source', 'source_display',
            'description', 'amount', 'revenue_date',
            'related_booking', 'booking_number',
            'related_payment',
            'created_at'
        ]
        read_only_fields = ['id', 'revenue_number', 'created_at']
    
    def get_booking_number(self, obj):
        if obj.related_booking:
            return obj.related_booking.booking_number
        return None


class FinancialReportSerializer(serializers.ModelSerializer):
    """Financial Report Serializer"""
    report_type_display = serializers.CharField(
        source='get_report_type_display',
        read_only=True
    )
    generated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'report_type', 'report_type_display',
            'report_date', 'start_date', 'end_date',
            'total_revenue', 'total_expenses', 'net_profit',
            'total_bookings', 'completed_bookings', 'cancelled_bookings',
            'total_rooms_available', 'occupancy_rate',
            'total_payments_received', 'pending_payments',
            'generated_by', 'generated_by_name',
            'report_file_url',
            'created_at'
        ]
        read_only_fields = [
            'id', 'net_profit', 'created_at'
        ]
    
    def get_generated_by_name(self, obj):
        if obj.generated_by:
            return obj.generated_by.get_full_name()
        return None


class FinancialReportCreateSerializer(serializers.ModelSerializer):
    """Financial Report Creation Serializer"""
    
    class Meta:
        model = FinancialReport
        fields = [
            'report_type', 'report_date',
            'start_date', 'end_date'
        ]
    
    def validate(self, attrs):
        """Validate dates"""
        if attrs['end_date'] < attrs['start_date']:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        return attrs
    
    def create(self, validated_data):
        """Create report with calculations"""
        from booking_api.models import Booking, Payment
        from room_management.models import Room
        from datetime import datetime
        
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        
        # Calculate metrics
        bookings = Booking.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_active=True
        )
        
        total_revenue = bookings.filter(
            payment_status='paid'
        ).aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        total_expenses = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lte=end_date,
            is_approved=True
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Create report
        report = FinancialReport.objects.create(
            generated_by=self.context['request'].user,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            total_bookings=bookings.count(),
            completed_bookings=bookings.filter(
                booking_status='checked_out'
            ).count(),
            cancelled_bookings=bookings.filter(
                booking_status='cancelled'
            ).count(),
            total_rooms_available=Room.objects.filter(
                is_active=True
            ).count(),
            **validated_data
        )
        
        return report