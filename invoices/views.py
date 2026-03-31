from decimal import Decimal
from datetime import date
from django.db.models import Sum, Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Customer, RecurringInvoiceTemplate
from .serializers import CustomerSerializer, RecurringInvoiceTemplateSerializer


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
def recurring_template_list_create(request):
    if request.method == 'GET':
        search = request.GET.get('search', '').strip()
        status_value = request.GET.get('status', '').strip()
        customer_id = request.GET.get('customer', '').strip()

        templates = RecurringInvoiceTemplate.objects.filter(
            user=request.user
        ).select_related('customer').order_by('-created_at')

        if search:
            templates = templates.filter(
                Q(template_id__icontains=search) |
                Q(template_name__icontains=search) |
                Q(customer__customer_name__icontains=search) |
                Q(customer__company_name__icontains=search)
            )

        if status_value:
            templates = templates.filter(status=status_value)

        if customer_id:
            templates = templates.filter(customer_id=customer_id)

        serializer = RecurringInvoiceTemplateSerializer(templates, many=True)
        return Response(serializer.data)

    serializer = RecurringInvoiceTemplateSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def recurring_template_detail(request, pk):
    try:
        template = RecurringInvoiceTemplate.objects.select_related('customer').get(pk=pk, user=request.user)
    except RecurringInvoiceTemplate.DoesNotExist:
        return Response({'error': 'Recurring invoice template not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RecurringInvoiceTemplateSerializer(template)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = RecurringInvoiceTemplateSerializer(
            template,
            data=request.data,
            partial=(request.method == 'PATCH'),
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    template.delete()
    return Response({'message': 'Template deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause_recurring_template(request, pk):
    try:
        template = RecurringInvoiceTemplate.objects.get(pk=pk, user=request.user)
    except RecurringInvoiceTemplate.DoesNotExist:
        return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)

    template.status = 'Paused'
    template.save(update_fields=['status', 'updated_at'])
    return Response({
        'message': 'Template paused successfully',
        'template_id': template.template_id,
        'status': template.status
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_recurring_template(request, pk):
    try:
        template = RecurringInvoiceTemplate.objects.get(pk=pk, user=request.user)
    except RecurringInvoiceTemplate.DoesNotExist:
        return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)

    template.status = 'Active'
    template.save(update_fields=['status', 'updated_at'])
    return Response({
        'message': 'Template activated successfully',
        'template_id': template.template_id,
        'status': template.status
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recurring_dashboard_summary(request):
    today = date.today()

    templates = RecurringInvoiceTemplate.objects.filter(user=request.user)

    total_templates = templates.count()
    active_templates = templates.filter(status='Active').count()

    due_in_7_days = templates.filter(
        status='Active',
        next_run_date__gte=today,
        next_run_date__lte=today.replace(day=today.day)  # dummy to avoid error? no
    ).count()

    # correct 7 day range
    from datetime import timedelta
    due_in_7_days = templates.filter(
        status='Active',
        next_run_date__gte=today,
        next_run_date__lte=today + timedelta(days=7)
    ).count()

    projected_monthly = templates.filter(
        status='Active'
    ).aggregate(total=Sum('cycle_amount'))['total'] or Decimal('0.00')

    return Response({
        'total_templates': total_templates,
        'active': active_templates,
        'due_in_7_days': due_in_7_days,
        'projected_monthly': projected_monthly
    })