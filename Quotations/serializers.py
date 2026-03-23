from rest_framework import serializers
from .models import Customer, Quotation, QuotationItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ['id', 'item_name', 'description', 'quantity', 'unit', 'price', 'tax_percent', 'total']
        read_only_fields = ['total']


class CustomerRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return value.pk

    def to_internal_value(self, data):
        request_user = self.context.get('request').user if self.context and self.context.get('request') else None

        # Accept direct id or name string
        if isinstance(data, str):
            if data.isdigit():
                try:
                    return Customer.objects.get(pk=int(data), user=request_user)
                except Customer.DoesNotExist:
                    raise serializers.ValidationError('Customer with id {0} does not exist.'.format(data))

            customer, created = Customer.objects.get_or_create(customer_name=data, user=request_user)
            return customer

        # Accept nested object by name/id
        if isinstance(data, dict):
            customer_name = data.get('customer_name') or data.get('name')
            customer_id = data.get('id')

            if customer_id is not None:
                try:
                    return Customer.objects.get(pk=customer_id, user=request_user)
                except Customer.DoesNotExist:
                    raise serializers.ValidationError('Customer with id {0} does not exist.'.format(customer_id))

            if customer_name:
                customer, created = Customer.objects.get_or_create(customer_name=customer_name, user=request_user)
                return customer

            raise serializers.ValidationError('Customer data must include id or customer_name.')

        return super().to_internal_value(data)


class QuotationSerializer(serializers.ModelSerializer):
    customer = CustomerRelatedField(queryset=Customer.objects.all())
    items = QuotationItemSerializer(many=True)

    class Meta:
        model = Quotation
        fields = [
            'id',
            'customer',
            'quotation_no',
            'quotation_date',
            'expiry_date',
            'status',
            'notes',
            'subtotal',
            'tax_amount',
            'discount_amount',
            'total_amount',
            'items',
            'created_at',
        ]
        read_only_fields = ['subtotal', 'total_amount', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        quotation = Quotation.objects.create(**validated_data)

        for item_data in items_data:
            QuotationItem.objects.create(quotation=quotation, **item_data)

        quotation.calculate_totals()
        return quotation

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        instance.customer = validated_data.get('customer', instance.customer)
        instance.quotation_no = validated_data.get('quotation_no', instance.quotation_no)
        instance.quotation_date = validated_data.get('quotation_date', instance.quotation_date)
        instance.expiry_date = validated_data.get('expiry_date', instance.expiry_date)
        instance.status = validated_data.get('status', instance.status)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.tax_amount = validated_data.get('tax_amount', instance.tax_amount)
        instance.discount_amount = validated_data.get('discount_amount', instance.discount_amount)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                QuotationItem.objects.create(quotation=instance, **item_data)

        instance.calculate_totals()
        return instance