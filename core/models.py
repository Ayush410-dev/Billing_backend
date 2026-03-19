from django.db import models
from django.contrib.auth import get_user_model


class RecurringInvoice(models.Model):

    Status_Choices = (
        ('Active', 'Active'),
        ('Paused', 'Paused'),
        ('Stop', 'Stop'),
    )

    Frequency_Choices = (
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),
    )

    recurring_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    customer_name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)

    frequency = models.CharField(max_length=20, choices=Frequency_Choices)

    Start_Date = models.DateField()
    End_Date = models.DateField()
    next_invoice_date = models.DateField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=Status_Choices, default='Active')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.recurring_id


class InvoiceItem(models.Model):

    invoice = models.ForeignKey(
        RecurringInvoice,
        related_name='items',
        on_delete=models.CASCADE
    )

    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = (self.quantity * self.rate) - self.discount
        super().save(*args, **kwargs)