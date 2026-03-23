from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('login.urls')),
    path('api/', include('core.urls')),
    path('api/', include('inventory.urls')),
    path('api/', include('vendorbills.urls')),
     path('api/', include('Quotations.urls')),
     path('api/delivery-challans/', include('DeliveryChallan.urls')),
]
     





