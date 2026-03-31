from django.contrib import admin
from .models import Customer, RecurringInvoiceTemplate


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'company_name', 'email', 'mobile', 'created_at']
    search_fields = ['customer_name', 'company_name', 'email', 'mobile']


@admin.register(RecurringInvoiceTemplate)
class RecurringInvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'template_id', 'template_name', 'customer', 'frequency',
        'interval_count', 'next_run_date', 'cycle_amount', 'status', 'auto_send'
    ]
    list_filter = ['status', 'frequency', 'auto_send', 'approval_required']
    search_fields = ['template_id', 'template_name', 'customer__customer_name', 'customer__company_name']