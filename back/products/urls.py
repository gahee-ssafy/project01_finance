from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend),      # AI 추천 
]
