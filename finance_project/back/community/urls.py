from django.urls import path
from . import views

urlpatterns = [
    # posts
    path('posts/', views.PostListCreateView.as_view(), name='post_list_create'),
    path('posts/<int:pk>/', views.PostRetrieveUpdateDestroyView.as_view(), name='post_detail'),

    # comments
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment_list_create'),
    path('comments/<int:pk>/', views.CommentRetrieveUpdateDestroyView.as_view(), name='comment_detail'),
]
