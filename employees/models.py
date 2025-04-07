from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=255)
    education = models.CharField(max_length=255)
    address = models.TextField()
    phone_no = models.CharField(max_length=15)
    employee_id = models.CharField(max_length=4, unique=True, editable=False)
    Salary = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        if not self.employee_id: 
            last_employee = Employee.objects.order_by('-id').first()
            if last_employee:
                self.employee_id = str(int(last_employee.employee_id) + 1).zfill(4)
            else:
                self.employee_id = "1111"  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"
