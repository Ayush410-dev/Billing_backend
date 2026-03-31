from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
import calendar

User = get_user_model()


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_customers')
    customer_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name


class RecurringInvoiceTemplate(models.Model):
    FREQUENCY_CHOICES = (
        ('Weekly', 'Weekly'),
        ('Bi-weekly', 'Bi-weekly'),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Yearly', 'Yearly'),
    )

    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Paused', 'Paused'),
        ('Cancelled', 'Cancelled'),
    )

    template_id = models.CharField(max_length=30, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_templates')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='recurring_templates')

    template_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    interval_count = models.PositiveIntegerField(default=1)

    start_date = models.DateField()
    next_run_date = models.DateField()
    due_days = models.PositiveIntegerField(default=0)

    cycle_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    auto_send = models.BooleanField(default=False)

    approval_required = models.BooleanField(default=False)
    email_reminder_before_due = models.BooleanField(default=False)
    overdue_followup = models.BooleanField(default=False)
    gst_enabled = models.BooleanField(default=False)
    ledger_tag = models.CharField(max_length=100, blank=True, null=True)
    po_number = models.CharField(max_length=100, blank=True, null=True)
    contract_reference = models.CharField(max_length=100, blank=True, null=True)
    auto_post_sales_ledger = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.template_id} - {self.template_name}"

    def calculate_next_run_date(self, from_date=None):
        if from_date is None:
            from_date = self.next_run_date

        if self.frequency == 'Weekly':
            return from_date + timedelta(days=7 * self.interval_count)

        if self.frequency == 'Bi-weekly':
            return from_date + timedelta(days=14 * self.interval_count)

        if self.frequency == 'Monthly':
            month = from_date.month - 1 + self.interval_count
            year = from_date.year + month // 12
            month = month % 12 + 1
            day = min(from_date.day, calendar.monthrange(year, month)[1])
            return date(year, month, day)

        if self.frequency == 'Quarterly':
            month = from_date.month - 1 + (3 * self.interval_count)
            year = from_date.year + month // 12
            month = month % 12 + 1
            day = min(from_date.day, calendar.monthrange(year, month)[1])
            return date(year, month, day)

        if self.frequency == 'Yearly':
            try:
                return from_date.replace(year=from_date.year + self.interval_count)
            except ValueError:
                return from_date.replace(month=2, day=28, year=from_date.year + self.interval_count)

        return from_date