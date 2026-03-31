from django.contrib import admin
from .models import Customer, Product, PosSale, PosSaleItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'company_name', 'mobile', 'created_at']
    search_fields = ['customer_name', 'company_name', 'mobile']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_name', 'sku', 'category', 'price', 'stock', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['product_name', 'sku']


class PosSaleItemInline(admin.TabularInline):
    model = PosSaleItem
    extra = 0
    readonly_fields = ['product_name', 'sku', 'quantity', 'unit_price', 'line_total']


@admin.register(PosSale)
class PosSaleAdmin(admin.ModelAdmin):
    list_display = ['sale_no', 'customer', 'payment_method', 'total', 'amount_received', 'change_due', 'created_at']
    search_fields = ['sale_no', 'customer__customer_name']
    inlines = [PosSaleItemInline]