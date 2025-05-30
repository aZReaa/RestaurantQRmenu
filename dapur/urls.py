from django.urls import path
from . import views

app_name = 'dapur'

urlpatterns = [
    path('', views.dapur_index, name='index'),
    path('order/<int:pesanan_id>/', views.order_detail, name='order_detail'),
    path('update-status/<int:pesanan_id>/', views.update_order_status, name='update_status'),
]
