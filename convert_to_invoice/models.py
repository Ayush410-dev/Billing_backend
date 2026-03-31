from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='convert_customers')
    customer_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name or self.customer_name


class InvoiceTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoice_templates')
    template_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.template_name


class SourceDocument(models.Model):
    SOURCE_CHOICES = (
        ('Quotation', 'Quotation'),
        ('Delivery Challan', 'Delivery Challan'),
        ('Sales Order', 'Sales Order'),
    )

    STATUS_CHOICES = (
        ('Pending Convert', 'Pending Convert'),
        ('Awaiting Approval', 'Awaiting Approval'),
        ('Rejected', 'Rejected'),
        ('Converted', 'Converted'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='source_documents')
    source_type = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    source_no = models.CharField(max_length=100, unique=True)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='source_documents')
    document_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending Convert')
    approval_required = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    is_converted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_type} - {self.source_no}"


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='converted_invoices')
    invoice_no = models.CharField(max_length=100, unique=True)

    source_document = models.OneToOneField(
        SourceDocument,
        on_delete=models.CASCADE,
        related_name='invoice'
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    invoice_template = models.ForeignKey(
        InvoiceTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )

    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_no


class ConversionLog(models.Model):
    ACTION_CHOICES = (
        ('Converted', 'Converted'),
        ('Rejected', 'Rejected'),
        ('Approved', 'Approved'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversion_logs')
    source_document = models.ForeignKey(SourceDocument, on_delete=models.CASCADE, related_name='conversion_logs')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversion_logs')

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    remarks = models.TextField(blank=True, null=True)
    action_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_document.source_no} - {self.action}"