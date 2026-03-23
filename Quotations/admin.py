from django.contrib import admin
from .models import Customer, Quotation, QuotationItem


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'email', 'mobile', 'created_at']
    search_fields = ['customer_name', 'email', 'mobile']


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['id', 'quotation_no', 'customer', 'quotation_date', 'status', 'total_amount']
    search_fields = ['quotation_no', 'customer__customer_name']
    list_filter = ['status', 'quotation_date']
    inlines = [QuotationItemInline]