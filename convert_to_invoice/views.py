from datetime import date
from decimal import Decimal, InvalidOperation

from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Customer, InvoiceTemplate, SourceDocument, Invoice, ConversionLog
from .serializers import (
    CustomerSerializer,
    InvoiceTemplateSerializer,
    SourceDocumentSerializer,
    InvoiceSerializer,
    ConversionLogSerializer,
)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def customer_list_create(request):
    if request.method == 'GET':
        customers = Customer.objects.filter(user=request.user).order_by('-created_at')
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def invoice_template_list_create(request):
    if request.method == 'GET':
        templates = InvoiceTemplate.objects.filter(user=request.user).order_by('-created_at')
        serializer = InvoiceTemplateSerializer(templates, many=True)
        return Response(serializer.data)

    serializer = InvoiceTemplateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def source_document_list_create(request):
    if request.method == 'GET':
        search = request.GET.get('search', '').strip()
        source_type = request.GET.get('source_type', '').strip()
        status_value = request.GET.get('status', '').strip()

        docs = SourceDocument.objects.filter(user=request.user).select_related('customer').order_by('-document_date')

        if search:
            docs = docs.filter(
                Q(source_no__icontains=search) |
                Q(customer__customer_name__icontains=search) |
                Q(customer__company_name__icontains=search)
            )

        if source_type:
            docs = docs.filter(source_type=source_type)

        if status_value:
            docs = docs.filter(status=status_value)

        serializer = SourceDocumentSerializer(docs, many=True)
        return Response(serializer.data)

    serializer = SourceDocumentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def source_document_detail(request, pk):
    try:
        doc = SourceDocument.objects.select_related('customer').get(pk=pk, user=request.user)
    except SourceDocument.DoesNotExist:
        return Response({'error': 'Source document not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SourceDocumentSerializer(doc)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convert_to_invoice(request, pk):
    try:
        source_doc = SourceDocument.objects.select_related('customer').get(pk=pk, user=request.user)
    except SourceDocument.DoesNotExist:
        return Response({'error': 'Source document not found'}, status=status.HTTP_404_NOT_FOUND)

    if source_doc.is_converted:
        return Response({'error': 'Document already converted'}, status=status.HTTP_400_BAD_REQUEST)

    if source_doc.status == 'Rejected':
        return Response({'error': 'Rejected document cannot be converted'}, status=status.HTTP_400_BAD_REQUEST)

    if source_doc.status == 'Awaiting Approval':
        return Response({'error': 'Document is awaiting approval'}, status=status.HTTP_400_BAD_REQUEST)

    template_id = request.data.get('invoice_template')
    invoice_date = request.data.get('invoice_date')
    due_date = request.data.get('due_date')
    remarks = request.data.get('remarks', '')

    try:
        tax_amount = Decimal(str(request.data.get('tax_amount', '0.00')))
    except (InvalidOperation, TypeError, ValueError):
        return Response({'error': 'Invalid tax_amount'}, status=status.HTTP_400_BAD_REQUEST)

    invoice_template = None
    if template_id:
        try:
            invoice_template = InvoiceTemplate.objects.get(pk=template_id, user=request.user)
        except InvoiceTemplate.DoesNotExist:
            return Response({'error': 'Invoice template not found'}, status=status.HTTP_404_NOT_FOUND)

    next_invoice_number = f"INV-{date.today().strftime('%Y%m%d')}-{Invoice.objects.filter(user=request.user).count() + 1:03d}"

    subtotal = source_doc.amount
    total_amount = subtotal + tax_amount

    invoice = Invoice.objects.create(
        user=request.user,
        invoice_no=next_invoice_number,
        source_document=source_doc,
        customer=source_doc.customer,
        invoice_template=invoice_template,
        invoice_date=invoice_date or date.today(),
        due_date=due_date or None,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        remarks=remarks,
    )

    source_doc.status = 'Converted'
    source_doc.is_converted = True
    source_doc.save(update_fields=['status', 'is_converted'])

    ConversionLog.objects.create(
        user=request.user,
        source_document=source_doc,
        invoice=invoice,
        action='Converted',
        remarks=remarks
    )

    serializer = InvoiceSerializer(invoice)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_source_document(request, pk):
    try:
        source_doc = SourceDocument.objects.get(pk=pk, user=request.user)
    except SourceDocument.DoesNotExist:
        return Response({'error': 'Source document not found'}, status=status.HTTP_404_NOT_FOUND)

    if source_doc.is_converted:
        return Response({'error': 'Converted document cannot be rejected'}, status=status.HTTP_400_BAD_REQUEST)

    source_doc.status = 'Rejected'
    source_doc.save(update_fields=['status'])

    ConversionLog.objects.create(
        user=request.user,
        source_document=source_doc,
        action='Rejected',
        remarks=request.data.get('remarks', '')
    )

    return Response({'message': 'Document rejected successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_source_document(request, pk):
    try:
        source_doc = SourceDocument.objects.get(pk=pk, user=request.user)
    except SourceDocument.DoesNotExist:
        return Response({'error': 'Source document not found'}, status=status.HTTP_404_NOT_FOUND)

    if source_doc.is_converted:
        return Response({'error': 'Converted document cannot be approved again'}, status=status.HTTP_400_BAD_REQUEST)

    source_doc.status = 'Pending Convert'
    source_doc.save(update_fields=['status'])

    ConversionLog.objects.create(
        user=request.user,
        source_document=source_doc,
        action='Approved',
        remarks=request.data.get('remarks', '')
    )

    return Response({'message': 'Document approved successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_list(request):
    invoices = Invoice.objects.filter(user=request.user).select_related(
        'customer', 'source_document', 'invoice_template'
    ).order_by('-created_at')

    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversion_log_list(request):
    logs = ConversionLog.objects.filter(user=request.user).select_related(
        'source_document', 'invoice'
    ).order_by('-action_at')

    serializer = ConversionLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def convert_dashboard_summary(request):
    docs = SourceDocument.objects.filter(user=request.user)

    pending_convert = docs.filter(status='Pending Convert').count()
    converted = docs.filter(status='Converted').count()
    awaiting_approval = docs.filter(status='Awaiting Approval').count()
    rejected = docs.filter(status='Rejected').count()

    return Response({
        'pending_convert': pending_convert,
        'converted': converted,
        'awaiting_approval': awaiting_approval,
        'rejected': rejected,
    })