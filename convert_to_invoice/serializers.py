from rest_framework import serializers
from .models import Customer, InvoiceTemplate, SourceDocument, Invoice, ConversionLog


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class InvoiceTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceTemplate
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class SourceDocumentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)

    class Meta:
        model = SourceDocument
        fields = [
            'id',
            'source_type',
            'source_no',
            'customer',
            'customer_name',
            'document_date',
            'amount',
            'status',
            'approval_required',
            'notes',
            'is_converted',
            'created_at',
        ]
        read_only_fields = ['user', 'is_converted', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    source_no = serializers.CharField(source='source_document.source_no', read_only=True)
    template_name = serializers.CharField(source='invoice_template.template_name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_no',
            'source_document',
            'source_no',
            'customer',
            'customer_name',
            'invoice_template',
            'template_name',
            'invoice_date',
            'due_date',
            'subtotal',
            'tax_amount',
            'total_amount',
            'remarks',
            'created_at',
        ]
        read_only_fields = ['user', 'created_at']


class ConversionLogSerializer(serializers.ModelSerializer):
    source_no = serializers.CharField(source='source_document.source_no', read_only=True)
    invoice_no = serializers.CharField(source='invoice.invoice_no', read_only=True)

    class Meta:
        model = ConversionLog
        fields = [
            'id',
            'source_document',
            'source_no',
            'invoice',
            'invoice_no',
            'action',
            'remarks',
            'action_at',
        ]
        read_only_fields = ['user', 'action_at']