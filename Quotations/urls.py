from django.urls import path
from . import views

urlpatterns = [
    path('quotations/', views.quotation_list_create),
]