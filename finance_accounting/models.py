
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, EmailValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q, F
from decimal import Decimal
import uuid
from datetime import timedelta
from authontication.models import TimeStampedModel, SoftDeleteModel
from authontication.models import User
from booking_api.models import Booking
from employees.models import Employee
from booking_api.models import Payment
from review.models import MaintenanceRequest


# ==========================================
# 10. FINANCE & ACCOUNTING MODELS
# ==========================================

class Invoice(SoftDeleteModel):
    """
    Invoice generation for bookings
    Finance team can view and manage all invoices
    """
    INVOICE_STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('paid', _('Paid')),
        ('partially_paid', _('Partially Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    )
    
    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )
    booking = models.OneToOneField(
        Booking,
        on_delete=models.PROTECT,
        related_name='invoice'
    )
    
    # Invoice details
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    
    # Amounts
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    
    # Notes
    notes = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    
    # PDF storage
    pdf_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Finance tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices'
    )
    
    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['issue_date', 'due_date']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.booking.booking_number}"
    
    def save(self, *args, **kwargs):
        # Auto-generate invoice number
        if not self.invoice_number:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d')
            count = Invoice.objects.filter(
                created_at__date=datetime.now().date()
            ).count() + 1
            self.invoice_number = f"INV{timestamp}{count:04d}"
        
        # Calculate total
        self.total_amount = (
            self.subtotal + 
            self.tax_amount - 
            self.discount_amount
        )
        
        # Update status based on payment
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partially_paid'
        
        super().save(*args, **kwargs)
    
    @property
    def balance_due(self):
        """Remaining amount to be paid"""
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status == 'paid':
            return False
        return timezone.now().date() > self.due_date


class InvoiceItem(SoftDeleteModel):
    """
    Individual line items in an invoice
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    class Meta:
        verbose_name = _('invoice item')
        verbose_name_plural = _('invoice items')
        db_table = 'invoice_items'
    
    def __str__(self):
        return f"{self.description} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate amount
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Expense(SoftDeleteModel):
    """
    Hotel expenses tracking
    Only Finance and Admin can create/edit
    """
    EXPENSE_CATEGORY_CHOICES = (
        ('salary', _('Salary & Wages')),
        ('utilities', _('Utilities')),
        ('maintenance', _('Maintenance & Repairs')),
        ('supplies', _('Supplies')),
        ('marketing', _('Marketing')),
        ('food_beverage', _('Food & Beverage')),
        ('insurance', _('Insurance')),
        ('taxes', _('Taxes')),
        ('rent', _('Rent/Lease')),
        ('other', _('Other')),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('partial', _('Partially Paid')),
    )
    
    expense_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )
    
    # Expense details
    category = models.CharField(
        max_length=30,
        choices=EXPENSE_CATEGORY_CHOICES,
        db_index=True
    )
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Date tracking
    expense_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    
    # Status
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Vendor/Supplier
    vendor_name = models.CharField(max_length=200, blank=True)
    
    # Related employee (if salary expense)
    related_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    
    # Related maintenance (if maintenance expense)
    related_maintenance = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    
    # Attachments
    receipt_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Finance tracking
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_expenses'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expenses'
    )
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('expense')
        verbose_name_plural = _('expenses')
        db_table = 'expenses'
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['expense_date', 'category']),
            models.Index(fields=['payment_status', 'is_approved']),
        ]
    
    def __str__(self):
        return f"{self.expense_number} - {self.category} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        # Auto-generate expense number
        if not self.expense_number:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.expense_number = f"EXP{timestamp}"
        
        super().save(*args, **kwargs)


class Revenue(SoftDeleteModel):
    """
    Revenue tracking - Auto-created from bookings
    Finance dashboard এর জন্য
    """
    REVENUE_SOURCE_CHOICES = (
        ('room_booking', _('Room Booking')),
        ('room_service', _('Room Service')),
        ('restaurant', _('Restaurant')),
        ('other', _('Other Services')),
    )
    
    revenue_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )
    
    # Source
    source = models.CharField(
        max_length=30,
        choices=REVENUE_SOURCE_CHOICES,
        default='room_booking',
        db_index=True
    )
    description = models.TextField(blank=True)
    
    # Amount
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Date
    revenue_date = models.DateField(db_index=True)
    
    # Related records
    related_booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revenues'
    )
    related_payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revenues'
    )
    
    class Meta:
        verbose_name = _('revenue')
        verbose_name_plural = _('revenues')
        db_table = 'revenues'
        ordering = ['-revenue_date']
        indexes = [
            models.Index(fields=['revenue_date', 'source']),
        ]
    
    def __str__(self):
        return f"{self.revenue_number} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        # Auto-generate revenue number
        if not self.revenue_number:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.revenue_number = f"REV{timestamp}"
        
        super().save(*args, **kwargs)


class FinancialReport(SoftDeleteModel):
    """
    Pre-calculated financial reports
    Finance team এর জন্য quick access
    """
    REPORT_TYPE_CHOICES = (
        ('daily', _('Daily Report')),
        ('weekly', _('Weekly Report')),
        ('monthly', _('Monthly Report')),
        ('quarterly', _('Quarterly Report')),
        ('yearly', _('Yearly Report')),
        ('custom', _('Custom Report')),
    )
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        db_index=True
    )
    report_date = models.DateField(db_index=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Financial summary
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    net_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Booking statistics
    total_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    cancelled_bookings = models.PositiveIntegerField(default=0)
    
    # Room statistics
    total_rooms_available = models.PositiveIntegerField(default=0)
    occupancy_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_("Percentage")
    )
    
    # Payment statistics
    total_payments_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    pending_payments = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Generated by
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports'
    )
    
    # Report file
    report_file_url = models.URLField(max_length=500, blank=True, null=True)
    
    class Meta:
        verbose_name = _('financial report')
        verbose_name_plural = _('financial reports')
        db_table = 'financial_reports'
        ordering = ['-report_date']
        indexes = [
            models.Index(fields=['report_type', 'report_date']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['report_type', 'report_date'],
                name='unique_report_per_date'
            )
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.report_date}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate net profit
        self.net_profit = self.total_revenue - self.total_expenses
        super().save(*args, **kwargs)