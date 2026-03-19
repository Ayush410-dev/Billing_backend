from django.urls import path
from .views import invoice_list

urlpatterns = [
    path('recurring-invoices/', invoice_list),
]