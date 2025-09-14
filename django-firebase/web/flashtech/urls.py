from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('client-screen/', views.client_screen, name='client_screen'),
    path('reset-client-screen/', views.reset_client_screen, name='reset_client_screen'),
    path('<str:order_id>/', views.order_detail, name='order_detail'),
    path('amount/<str:order_id>/', views.record_amount_paid, name='record_amount_paid'),

]
