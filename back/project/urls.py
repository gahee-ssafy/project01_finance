from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # products
    path('api/v1/products/', include('products.urls')),
]
