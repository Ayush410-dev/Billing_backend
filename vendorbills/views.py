from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Vendor, VendorBill
from .serializers import VendorSerializer, VendorBillSerializer


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def vendor_list(request):
    vendors = Vendor.objects.filter(user=request.user, is_active=True).order_by('vendor_name')
    serializer = VendorSerializer(vendors, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vendor_bill_list_create(request):
    if request.method == 'GET':
        search = request.GET.get('search', '').strip()
        vendor_id = request.GET.get('vendor', '').strip()
        status_value = request.GET.get('status', '').strip()

        bills = VendorBill.objects.filter(user=request.user).select_related('vendor').order_by('-created_at')

        if search:
            bills = bills.filter(
                Q(bill_no__icontains=search) |
                Q(po_grn__icontains=search) |
                Q(vendor__vendor_name__icontains=search)
            )

        if vendor_id:
            bills = bills.filter(vendor_id=vendor_id)

        if status_value:
            bills = bills.filter(status=status_value)

        serializer = VendorBillSerializer(bills, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = VendorBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_bill_detail(request, pk):
    try:
        bill = VendorBill.objects.select_related('vendor').get(pk=pk, user=request.user)
    except VendorBill.DoesNotExist:
        return Response({"error": "Vendor bill not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = VendorBillSerializer(bill)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def vendor_bill_update_delete(request, pk):
    try:
        bill = VendorBill.objects.get(pk=pk, user=request.user)
    except VendorBill.DoesNotExist:
        return Response({"error": "Vendor bill not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = VendorBillSerializer(bill, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        bill.delete()
        return Response({"message": "Vendor bill deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_bill_summary(request):
    bills = VendorBill.objects.filter(user=request.user)

    total_bills = bills.count()
    total_amount = bills.aggregate(
        total=Coalesce(Sum('amount'), 0)
    )['total']
    total_paid = bills.aggregate(
        total=Coalesce(Sum('paid_amount'), 0)
    )['total']
    total_payable = bills.aggregate(
        total=Coalesce(Sum('balance'), 0)
    )['total']

    return Response({
        "vendor_bills": total_bills,
        "total_amount": total_amount,
        "paid": total_paid,
        "payable": total_payable
    })