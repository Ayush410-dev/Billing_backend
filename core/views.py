from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import RecurringInvoice
from .Serializers import RecurringInvoiceSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])  
@permission_classes([IsAuthenticated])
def invoice_list(request):

    if request.method == 'GET':
        invoices = RecurringInvoice.objects.filter(user=request.user)
        serializer = RecurringInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = RecurringInvoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)