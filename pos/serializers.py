from rest_framework import serializers
from .models import Customer, Product, PosSale, PosSaleItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class PosSaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PosSaleItem
        fields = [
            'id',
            'product',
            'product_name',
            'sku',
            'batch',
            'quantity',
            'unit_price',
            'line_total',
        ]
        read_only_fields = ['product_name', 'sku', 'unit_price', 'line_total']


class PosSaleSerializer(serializers.ModelSerializer):
    items = PosSaleItemSerializer(many=True)
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)

    class Meta:
        model = PosSale
        fields = [
            'id',
            'sale_no',
            'customer',
            'customer_name',
            'payment_method',
            'discount_percent',
            'tax_percent',
            'subtotal',
            'discount_amount',
            'tax_amount',
            'total',
            'amount_received',
            'change_due',
            'notes',
            'items',
            'created_at',
        ]
        read_only_fields = [
            'sale_no',
            'subtotal',
            'discount_amount',
            'tax_amount',
            'total',
            'change_due',
            'created_at',
        ]