from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from inventory.models import Vendor

User = get_user_model()


class VendorBill(models.Model):
    STATUS_CHOICES = (
        ('Unpaid', 'Unpaid'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_bills')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_bills')

    bill_no = models.CharField(max_length=100, unique=True)
    po_grn = models.CharField(max_length=100, blank=True, null=True)
    bill_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.balance = Decimal(self.amount) - Decimal(self.paid_amount)

        if self.paid_amount <= 0:
            self.status = 'Unpaid'
        elif self.paid_amount < self.amount:
            self.status = 'Partially Paid'
        else:
            self.status = 'Paid'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.bill_no