from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # accounts
    path('api/v1/accounts/', include('accounts.urls')),

    # mypage
    # path('api/v1/mypage/', include('mypage.urls'))

    # community
    path('api/v1/community/', include('community.urls')),

    # products
    path('api/v1/products/', include('products.urls')),


]
