from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Customer, Quotation
from .serializers import CustomerSerializer, QuotationSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def customer_list_create(request):
    if request.method == 'GET':
        customers = Customer.objects.filter(user=request.user).order_by('-id')
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def quotation_list_create(request):
    if request.method == 'GET':
        search = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', '').strip()
        customer_id = request.GET.get('customer', '').strip()

        quotations = Quotation.objects.filter(user=request.user).select_related('customer').prefetch_related('items').order_by('-id')

        if search:
            quotations = quotations.filter(
                Q(quotation_no__icontains=search) |
                Q(customer__customer_name__icontains=search)
            )

        if status_filter:
            quotations = quotations.filter(status=status_filter)

        if customer_id:
            quotations = quotations.filter(customer_id=customer_id)

        serializer = QuotationSerializer(quotations, many=True, context={'request': request})
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = QuotationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def quotation_detail(request, pk):
    quotation = get_object_or_404(
        Quotation.objects.select_related('customer').prefetch_related('items'),
        pk=pk,
        user=request.user
    )

    if request.method == 'GET':
        serializer = QuotationSerializer(quotation, context={'request': request})
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = QuotationSerializer(quotation, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        quotation.delete()
        return Response({"message": "Quotation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)