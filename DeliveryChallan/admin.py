from django.contrib import admin
from .models import DeliveryChallan, DeliveryChallanItem


class DeliveryChallanItemInline(admin.TabularInline):
    model = DeliveryChallanItem
    extra = 1


@admin.register(DeliveryChallan)
class DeliveryChallanAdmin(admin.ModelAdmin):
    list_display = [
        'challan_no',
        'customer_name',
        'company_name',
        'challan_date',
        'status',
        'total_qty',
        'total_value'
    ]
    list_filter = ['status', 'challan_date']
    search_fields = ['challan_no', 'customer_name', 'company_name', 'reference_no', 'vehicle_no']
    inlines = [DeliveryChallanItemInline]