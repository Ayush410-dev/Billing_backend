from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import Customer, Product, PosSale
from .serializers import CustomerSerializer, ProductSerializer, PosSaleSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def customer_list_create(request):
    if request.method == 'GET':
        customers = Customer.objects.filter(user=request.user).order_by('customer_name')
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list_create(request):
    if request.method == 'GET':
        search = request.GET.get('search', '').strip()
        category = request.GET.get('category', '').strip()
        sku = request.GET.get('sku', '').strip()

        products = Product.objects.filter(user=request.user, is_active=True).order_by('-created_at')

        if search:
            products = products.filter(
                Q(product_name__icontains=search) |
                Q(sku__icontains=search)
            )

        if sku:
            products = products.filter(sku__icontains=sku)

        if category:
            products = products.filter(category=category)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk, user=request.user)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pos_checkout(request):
    serializer = PosSaleSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        sale = serializer.save()
        return Response(PosSaleSerializer(sale).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pos_sale_list(request):
    sales = PosSale.objects.filter(user=request.user).select_related('customer').prefetch_related('items').order_by('-created_at')
    serializer = PosSaleSerializer(sales, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pos_dashboard_summary(request):
    products = Product.objects.filter(user=request.user, is_active=True)
    out_of_stock = products.filter(stock=0).count()
    low_stock = products.filter(stock__gt=0, stock__lte=5).count()
    total_products = products.count()

    sales = PosSale.objects.filter(user=request.user)
    total_sales = sales.count()

    return Response({
        'total_products': total_products,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'total_sales': total_sales,
    })