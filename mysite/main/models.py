from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount_owed = models.PositiveIntegerField(default=0)
    amount_due = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Bill(models.Model):
    name = models.CharField(max_length=255)  # Name of the bill (e.g., "Dinner at XYZ")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount of the bill
    tip_percentage = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # User who created the bill
    created_at = models.DateTimeField(auto_now_add=True)

class BillSplit(models.Model):
    bill = models.ForeignKey(Bill, related_name="splits", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="bill_splits", on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)  # Amount the user owes for the bill

    def __str__(self):
        return f"{self.user.username} owes ${self.amount_owed} for {self.bill.name}"