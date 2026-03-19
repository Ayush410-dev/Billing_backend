from django.urls import path
from .views import (
    vendor_list,
    vendor_bill_list_create,
    vendor_bill_detail,
    vendor_bill_update_delete,
    vendor_bill_summary,
)

urlpatterns = [
    path('vendors/', vendor_list, name='vendor-list'),
    path('vendorbills/', vendor_bill_list_create, name='vendorbill-list-create'),
    path('vendorbills/summary/', vendor_bill_summary, name='vendorbill-summary'),
    path('vendorbills/<int:pk>/', vendor_bill_detail, name='vendorbill-detail'),
    path('vendorbills/<int:pk>/edit/', vendor_bill_update_delete, name='vendorbill-update-delete'),
]