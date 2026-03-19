from rest_framework import serializers
from .models import RecurringInvoice


class RecurringInvoiceSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = RecurringInvoice
        fields = '__all__'
        read_only_fields = [ 'user']
        
        