from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('new/', views.post_create, name='post_create'),
    path('<str:post_id>/', views.post_detail, name='post_detail'),
    path('<str:post_id>/edit/', views.post_update, name='post_update'),
    path('<str:post_id>/delete/', views.post_delete, name='post_delete'),
]
