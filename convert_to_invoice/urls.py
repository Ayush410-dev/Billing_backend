from django.urls import path
from .views import (
    customer_list_create,
    invoice_template_list_create,
    source_document_list_create,
    source_document_detail,
    convert_to_invoice,
    reject_source_document,
    approve_source_document,
    invoice_list,
    conversion_log_list,
    convert_dashboard_summary,
)

urlpatterns = [
    path('customers/', customer_list_create, name='convert-customer-list-create'),
    path('invoice-templates/', invoice_template_list_create, name='invoice-template-list-create'),

    path('source-documents/', source_document_list_create, name='source-document-list-create'),
    path('source-documents/<int:pk>/', source_document_detail, name='source-document-detail'),

    path('source-documents/<int:pk>/convert/', convert_to_invoice, name='convert-to-invoice'),
    path('source-documents/<int:pk>/reject/', reject_source_document, name='reject-source-document'),
    path('source-documents/<int:pk>/approve/', approve_source_document, name='approve-source-document'),

    path('invoices/', invoice_list, name='invoice-list'),
    path('conversion-logs/', conversion_log_list, name='conversion-log-list'),
    path('dashboard-summary/', convert_dashboard_summary, name='convert-dashboard-summary'),
]