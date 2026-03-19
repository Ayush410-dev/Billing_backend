from rest_framework import serializers
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, PurchaseOrderAuditLog


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'item_name', 'quantity', 'unit_price', 'line_total']
        read_only_fields = ['line_total']


class PurchaseOrderAuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = PurchaseOrderAuditLog
        fields = ['id', 'time', 'user', 'user_name', 'action', 'entity', 'notes']
        read_only_fields = ['time']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    vendor_name = serializers.CharField(source='vendor.vendor_name', read_only=True)
    total_qty = serializers.ReadOnlyField()
    audit_logs = PurchaseOrderAuditLogSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'user', 'vendor', 'vendor_name',
            'po_number', 'order_date', 'expected_date',
            'shipping_address', 'payment_terms', 'notes',
            'subtotal', 'total_amount', 'total_qty',
            'status', 'approval_status',
            'items', 'audit_logs',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'user', 'po_number', 'subtotal',
            'total_amount', 'total_qty',
            'created_at', 'updated_at',
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)
        purchase_order.update_totals()

        request = self.context.get('request')
        PurchaseOrderAuditLog.objects.create(
            purchase_order=purchase_order,
            user=request.user if request else None,
            action='Purchase Order Created',
            entity=purchase_order.po_number,
            notes=f"Status: {purchase_order.status} | Approval: {purchase_order.approval_status}"
        )
        return purchase_order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        old_status = instance.status
        old_approval = instance.approval_status

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseOrderItem.objects.create(purchase_order=instance, **item_data)
        instance.update_totals()

        request = self.context.get('request')
        changes = []
        if old_status != instance.status:
            changes.append(f"Status: {old_status} → {instance.status}")
        if old_approval != instance.approval_status:
            changes.append(f"Approval: {old_approval} → {instance.approval_status}")
        if changes:
            PurchaseOrderAuditLog.objects.create(
                purchase_order=instance,
                user=request.user if request else None,
                action='Purchase Order Updated',
                entity=instance.po_number,
                notes=", ".join(changes)
            )
        return instance

    def validate(self, attrs):
        order_date = attrs.get('order_date', getattr(self.instance, 'order_date', None))
        expected_date = attrs.get('expected_date', getattr(self.instance, 'expected_date', None))
        if expected_date and order_date and expected_date < order_date:
            raise serializers.ValidationError({
                'expected_date': 'Expected date cannot be earlier than order date.'
            })
        return attrs


class PurchaseOrderSummarySerializer(serializers.Serializer):
    """UI ke 4 top cards ke liye"""
    total_orders = serializers.IntegerField()
    open_orders = serializers.IntegerField()
    partial_orders = serializers.IntegerField()
    received_orders = serializers.IntegerField()
