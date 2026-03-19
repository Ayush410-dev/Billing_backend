from rest_framework import serializers
from .models import Vendor, VendorBill


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            'id',
            'vendor_name',
            'company_name',
            'email',
            'mobile',
            'address',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class VendorBillSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.vendor_name', read_only=True)

    class Meta:
        model = VendorBill
        fields = [
            'id',
            'vendor',
            'vendor_name',
            'bill_no',
            'po_grn',
            'bill_date',
            'amount',
            'paid_amount',
            'balance',
            'status',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'balance', 'status', 'created_at']