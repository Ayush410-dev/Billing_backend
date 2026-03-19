from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

User = get_user_model()


class Vendor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendors')
    vendor_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vendor_name


class PurchaseOrder(models.Model):
    PAYMENT_TERMS_CHOICES = (
        ('7 Days', '7 Days'),
        ('15 Days', '15 Days'),
        ('30 Days', '30 Days'),
        ('45 Days', '45 Days'),
        ('60 Days', '60 Days'),
    )

    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Open', 'Open'),
        ('Partially Received', 'Partially Received'),
        ('Received', 'Received'),
        ('Cancelled', 'Cancelled'),
    )

    APPROVAL_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchase_orders')
    po_number = models.CharField(max_length=50, unique=True, blank=True)
    order_date = models.DateField()
    expected_date = models.DateField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='30 Days')
    notes = models.TextField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_po_number(self):
        today = date.today().strftime('%y%m%d')
        last_po = PurchaseOrder.objects.filter(
            po_number__startswith=f'PO-{today}'
        ).order_by('-id').first()
        if last_po and last_po.po_number:
            try:
                last_sequence = int(last_po.po_number.split('-')[-1])
                new_sequence = last_sequence + 1
            except Exception:
                new_sequence = 1
        else:
            new_sequence = 1
        return f'PO-{today}-{new_sequence:03d}'

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = self.generate_po_number()
        super().save(*args, **kwargs)

    def update_totals(self):
        items = self.items.all()
        subtotal = sum([item.line_total for item in items], Decimal('0.00'))
        self.subtotal = subtotal
        self.total_amount = subtotal
        self.save(update_fields=['subtotal', 'total_amount', 'updated_at'])

    @property
    def total_qty(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return self.po_number


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='items'
    )
    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.line_total = Decimal(self.quantity) * Decimal(self.unit_price)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item_name


class PurchaseOrderAuditLog(models.Model):
    """UI mein 'Purchase Order Audit Log' table ke liye"""
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='audit_logs'
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    entity = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return f"{self.purchase_order} - {self.action}"