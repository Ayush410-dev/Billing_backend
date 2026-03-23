from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    customer_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name


class Quotation(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotations')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='quotations')
    quotation_no = models.CharField(max_length=100, unique=True)
    quotation_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    notes = models.TextField(blank=True, null=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_totals(self):
        items = self.items.all()
        subtotal = sum([item.total for item in items], Decimal('0.00'))
        self.subtotal = subtotal
        self.total_amount = subtotal + self.tax_amount - self.discount_amount
        self.save()

    def __str__(self):
        return self.quotation_no


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        base_amount = self.quantity * self.price
        tax_value = (base_amount * self.tax_percent) / Decimal('100.00')
        self.total = base_amount + tax_value
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item_name