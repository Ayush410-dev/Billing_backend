from rest_framework import serializers
from .models import Customer, RecurringInvoiceTemplate


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class RecurringInvoiceTemplateSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    company_name = serializers.CharField(source='customer.company_name', read_only=True)
    schedule_display = serializers.SerializerMethodField()

    class Meta:
        model = RecurringInvoiceTemplate
        fields = [
            'id',
            'template_id',
            'user',
            'customer',
            'customer_name',
            'company_name',
            'template_name',
            'description',
            'frequency',
            'interval_count',
            'schedule_display',
            'start_date',
            'next_run_date',
            'due_days',
            'cycle_amount',
            'auto_send',
            'approval_required',
            'email_reminder_before_due',
            'overdue_followup',
            'gst_enabled',
            'ledger_tag',
            'po_number',
            'contract_reference',
            'auto_post_sales_ledger',
            'status',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_schedule_display(self, obj):
        return f"Every {obj.interval_count} {obj.frequency}"

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)