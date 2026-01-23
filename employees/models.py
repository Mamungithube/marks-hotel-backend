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


# ==========================================
# 5. EMPLOYEE MANAGEMENT MODELS
# ==========================================

class Department(SoftDeleteModel):
    """
    Hotel departments - Housekeeping, Front Desk, Kitchen etc.
    """
    name = models.CharField(_('department name'), max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )
    
    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')
        db_table = 'departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Designation(SoftDeleteModel):
    """
    Job positions - Manager, Receptionist, Housekeeper etc.
    """
    title = models.CharField(_('designation title'), max_length=100, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='designations'
    )
    description = models.TextField(blank=True)
    level = models.PositiveIntegerField(
        default=1,
        help_text=_("Hierarchy level: 1=Entry, 5=Senior")
    )
    
    class Meta:
        verbose_name = _('designation')
        verbose_name_plural = _('designations')
        db_table = 'designations'
        ordering = ['department', 'level']
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"


class Employee(SoftDeleteModel):
    """
    Employee details - User model extend করে
    """
    EMPLOYMENT_TYPE_CHOICES = (
        ('full_time', _('Full Time')),
        ('part_time', _('Part Time')),
        ('contract', _('Contract')),
        ('intern', _('Intern')),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    employee_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        db_index=True
    )
    
    # Job details
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='employees'
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.PROTECT,
        related_name='employees'
    )
    
    # Employment info
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time'
    )
    joining_date = models.DateField(_('joining date'))
    resignation_date = models.DateField(null=True, blank=True)
    
    # Salary
    basic_salary = models.DecimalField(
        _('basic salary'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Contact (additional to User model)
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    # Documents
    national_id = models.CharField(max_length=50, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    
    # Education (from your old model)
    education = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = _('employee')
        verbose_name_plural = _('employees')
        db_table = 'employees'
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['department', 'designation']),
            models.Index(fields=['employee_id', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Auto-generate employee ID
        if not self.employee_id:
            last_employee = Employee.objects.order_by('-created_at').first()
            if last_employee and last_employee.employee_id:
                last_number = int(last_employee.employee_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.employee_id = f"EMP{new_number:05d}"
        
        super().save(*args, **kwargs)


class Shift(SoftDeleteModel):
    """
    Work shifts - Morning, Evening, Night
    """
    name = models.CharField(max_length=50, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        verbose_name = _('shift')
        verbose_name_plural = _('shifts')
        db_table = 'shifts'
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"