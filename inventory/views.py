from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vendor, PurchaseOrder
from .serializers import (
    VendorSerializer, PurchaseOrderSerializer, PurchaseOrderSummarySerializer
)


class VendorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = VendorSerializer

    def get_queryset(self):
        return Vendor.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'approval_status', 'vendor']
    search_fields = ['po_number', 'vendor__vendor_name']

    def get_queryset(self):
        return PurchaseOrder.objects.filter(
            user=self.request.user
        ).select_related('vendor').prefetch_related('items', 'audit_logs').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """UI ke 4 top cards — Total Orders, Open, Partial, Received"""
        qs = self.get_queryset()
        data = {
            'total_orders': qs.count(),
            'open_orders': qs.filter(status='Open').count(),
            'partial_orders': qs.filter(status='Partially Received').count(),
            'received_orders': qs.filter(status='Received').count(),
        }
        return Response(PurchaseOrderSummarySerializer(data).data)

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """UI mein Export button ke liye"""
        qs = self.get_queryset()
        status = request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
