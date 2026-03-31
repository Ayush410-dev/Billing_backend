from django.urls import path
from .views import (
    customer_list_create,
    recurring_template_list_create,
    recurring_template_detail,
    pause_recurring_template,
    activate_recurring_template,
    recurring_dashboard_summary,
)

urlpatterns = [
    path('customers/', customer_list_create, name='recurring-customer-list-create'),

    path('templates/', recurring_template_list_create, name='recurring-template-list-create'),
    path('templates/<int:pk>/', recurring_template_detail, name='recurring-template-detail'),

    path('templates/<int:pk>/pause/', pause_recurring_template, name='pause-recurring-template'),
    path('templates/<int:pk>/activate/', activate_recurring_template, name='activate-recurring-template'),

    path('dashboard-summary/', recurring_dashboard_summary, name='recurring-dashboard-summary'),
]