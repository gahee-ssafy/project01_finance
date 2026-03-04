from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.deposit_products), # 예적금 조회
    path("deposit/<str:fin_prdt_cd>/join/", views.deposit_join), # 필터링,정렬되게끔 추가
    path("deposit/<str:fin_prdt_cd>/", views.deposit_detail), # 목록 상세조회
    path('spot/', views.spot_price),          # 현물(금/은) 조회
    path('recommend/', views.recommend),      # AI 추천 
]
