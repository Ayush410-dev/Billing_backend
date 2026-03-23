from django.urls import path
from .views import (
    delivery_challan_list_create,
    delivery_challan_detail,
    delivery_challan_dashboard,
)

urlpatterns = [
    path('', delivery_challan_list_create, name='delivery-challan-list-create'),
    path('dashboard/', delivery_challan_dashboard, name='delivery-challan-dashboard'),
    path('<int:pk>/', delivery_challan_detail, name='delivery-challan-detail'),
]