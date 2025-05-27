from django.urls import path
from . import views

app_name = 'kasir'

urlpatterns = [
    path('', views.kasir_index, name='kasir_index'),
    path('dapur/', views.dapur_view, name='dapur'),
    path('kasir_dashboard/', views.kasir_dashboard, name='kasir_dashboard'),
    path('kasir_meja/<str:nomor_meja>/', views.detail_pesanan_meja, name='detail_pesanan_meja'),
    path('api/update-status-pesanan/<int:pesanan_id>/', views.update_status_pesanan, name='update_status_pesanan'),
    path('print-receipt/<int:pesanan_id>/', views.print_receipt, name='print_receipt'),
]
