from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import DeliveryChallan
from .serializers import DeliveryChallanSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def delivery_challan_list_create(request):
    if request.method == 'GET':
        search = request.GET.get('search', '').strip()
        status_value = request.GET.get('status', '').strip()

        challans = DeliveryChallan.objects.filter(user=request.user).prefetch_related('items')

        if search:
            challans = challans.filter(
                Q(challan_no__icontains=search) |
                Q(reference_no__icontains=search) |
                Q(vehicle_no__icontains=search) |
                Q(transporter_name__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(company_name__icontains=search)
            )

        if status_value:
            challans = challans.filter(status=status_value)

        challans = challans.order_by('-challan_date', '-id')
        serializer = DeliveryChallanSerializer(challans, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = DeliveryChallanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def delivery_challan_detail(request, pk):
    try:
        challan = DeliveryChallan.objects.prefetch_related('items').get(pk=pk, user=request.user)
    except DeliveryChallan.DoesNotExist:
        return Response({'error': 'Delivery Challan not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DeliveryChallanSerializer(challan)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = DeliveryChallanSerializer(
            challan,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        challan.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delivery_challan_dashboard(request):
    challans = DeliveryChallan.objects.filter(user=request.user)

    return Response({
        'total_challans': challans.count(),
        'dispatched': challans.filter(status='Dispatched').count(),
        'delivered': challans.filter(status='Delivered').count(),
        'draft_pending': challans.filter(status='Draft').count(),
    })