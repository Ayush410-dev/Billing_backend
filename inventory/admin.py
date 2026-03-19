from django.contrib import admin
from .models import Vendor, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor_name', 'company_name', 'email', 'mobile', 'is_active', 'created_at']
    search_fields = ['vendor_name', 'company_name', 'email', 'mobile']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'po_number', 'vendor', 'order_date', 'expected_date', 'payment_terms', 'subtotal', 'total_amount', 'status']
    search_fields = ['po_number', 'vendor__vendor_name']
    list_filter = ['status', 'payment_terms', 'order_date']
    inlines = [PurchaseOrderItemInline]