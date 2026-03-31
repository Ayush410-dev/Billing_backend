from django.urls import path
from .views import (
    customer_list_create,
    product_list_create,
    product_detail,
    pos_checkout,
    pos_sale_list,
    pos_dashboard_summary,
)

urlpatterns = [
    path('customers/', customer_list_create, name='pos-customer-list-create'),
    path('products/', product_list_create, name='pos-product-list-create'),
    path('products/<int:pk>/', product_detail, name='pos-product-detail'),

    path('checkout/', pos_checkout, name='pos-checkout'),
    path('sales/', pos_sale_list, name='pos-sale-list'),
    path('dashboard-summary/', pos_dashboard_summary, name='pos-dashboard-summary'),
]