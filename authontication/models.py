from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    image = models.CharField(max_length=100 , default='')
    email = models.CharField(max_length = 30)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
class CustomUser(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    def __str__(self):
        return self.username.username