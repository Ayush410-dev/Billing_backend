from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('login.urls')),
    path('api/core/', include('core.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/vendor-bills/', include('vendorbills.urls')),
    path('api/quotations/', include('Quotations.urls')),
    path('api/delivery-challans/', include('DeliveryChallan.urls')),
    path('api/invoices/', include('invoices.urls')),
    path('api/convert/', include('convert_to_invoice.urls')),
    path('api/pos/', include('pos.urls')),
]