from django.urls import path, include
from .views import CustomRegisterView

urlpatterns = [
    # dj_rest_auth 라이브러리 사용 
    # login/, logout/ 외 3건
    path('', include('dj_rest_auth.urls')),
    
    # 회원가입
    path('signup/', views.CustomRegisterView, name='signup')

]
