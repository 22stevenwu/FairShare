from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount_owed = models.PositiveIntegerField(default=0)
    amount_due = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
class Bill(models.Model):
    name = models.CharField(max_length=255)  
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    tip_percentage = models.PositiveIntegerField(default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  
    created_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=True)
    total_owed = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class BillSplit(models.Model):
    bill = models.ForeignKey(Bill, related_name="splits", on_delete=models.CASCADE)
    participant_name = models.CharField(max_length=255) 
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2)  
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False) 