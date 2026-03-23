from rest_framework import serializers
from .models import DeliveryChallan, DeliveryChallanItem


class DeliveryChallanItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryChallanItem
        fields = [
            'id',
            'item_name',
            'description',
            'quantity',
            'unit',
            'rate',
            'total',
        ]
        read_only_fields = ['total']


class DeliveryChallanSerializer(serializers.ModelSerializer):
    items = DeliveryChallanItemSerializer(many=True)

    class Meta:
        model = DeliveryChallan
        fields = [
            'id',
            'challan_no',
            'customer_name',
            'company_name',
            'challan_date',
            'reference_no',
            'vehicle_no',
            'transporter_name',
            'delivery_address',
            'notes',
            'status',
            'total_qty',
            'total_value',
            'items',
            'created_at',
        ]
        read_only_fields = ['challan_no', 'total_qty', 'total_value', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        challan = DeliveryChallan.objects.create(**validated_data)

        for item_data in items_data:
            DeliveryChallanItem.objects.create(challan=challan, **item_data)

        challan.update_totals()
        return challan

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                DeliveryChallanItem.objects.create(challan=instance, **item_data)

        instance.update_totals()
        return instance