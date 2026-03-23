from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class DeliveryChallan(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
    )

    challan_no = models.CharField(max_length=50, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_challans')

    customer_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)

    challan_date = models.DateField(default=timezone.now)
    reference_no = models.CharField(max_length=100, blank=True, null=True)

    vehicle_no = models.CharField(max_length=30, blank=True, null=True)
    transporter_name = models.CharField(max_length=255, blank=True, null=True)

    delivery_address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    total_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-challan_date', '-created_at']

    def __str__(self):
        return self.challan_no

    def save(self, *args, **kwargs):
        if not self.challan_no:
            today = timezone.now()
            prefix = f"DC-{today.strftime('%y%m%d')}"
            last_record = DeliveryChallan.objects.filter(
                challan_no__startswith=prefix
            ).order_by('-id').first()

            if last_record and last_record.challan_no:
                try:
                    last_number = int(last_record.challan_no.split('-')[-1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1

            self.challan_no = f"{prefix}-{str(new_number).zfill(3)}"

        super().save(*args, **kwargs)

    def update_totals(self):
        items = self.items.all()
        total_qty = sum([item.quantity for item in items], Decimal('0.00'))
        total_value = sum([item.total for item in items], Decimal('0.00'))

        self.total_qty = total_qty
        self.total_value = total_value
        self.save(update_fields=['total_qty', 'total_value'])


class DeliveryChallanItem(models.Model):
    challan = models.ForeignKey(
        DeliveryChallan,
        on_delete=models.CASCADE,
        related_name='items'
    )

    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='Nos')
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.item_name

    def save(self, *args, **kwargs):
        self.total = Decimal(self.quantity) * Decimal(self.rate)
        super().save(*args, **kwargs)