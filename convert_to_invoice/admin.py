from django.contrib import admin
from .models import Customer, InvoiceTemplate, SourceDocument, Invoice, ConversionLog


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'company_name', 'email', 'mobile', 'created_at']
    search_fields = ['customer_name', 'company_name', 'email']


@admin.register(InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'template_name', 'is_active', 'created_at']
    search_fields = ['template_name']


@admin.register(SourceDocument)
class SourceDocumentAdmin(admin.ModelAdmin):
    list_display = ['source_type', 'source_no', 'customer', 'document_date', 'amount', 'status', 'is_converted']
    list_filter = ['source_type', 'status', 'is_converted']
    search_fields = ['source_no', 'customer__customer_name', 'customer__company_name']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_no', 'source_document', 'customer', 'invoice_date', 'total_amount', 'created_at']
    search_fields = ['invoice_no', 'source_document__source_no', 'customer__customer_name']


@admin.register(ConversionLog)
class ConversionLogAdmin(admin.ModelAdmin):
    list_display = ['source_document', 'invoice', 'action', 'action_at']
    list_filter = ['action']