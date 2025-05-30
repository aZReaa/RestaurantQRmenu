from django.urls import path
from . import views

app_name = 'kasir'

urlpatterns = [
    path('', views.kasir_index, name='kasir_index'),
    path('kasir_meja/<str:nomor_meja>/', views.detail_pesanan_meja, name='detail_pesanan_meja'),
    path('process-payment/<int:pesanan_id>/', views.process_payment, name='process_payment'),
    path('api/update-status-pesanan/<int:pesanan_id>/', views.update_status_pesanan, name='update_status_pesanan'),
    path('print-receipt/<int:pesanan_id>/', views.print_receipt, name='print_receipt'),
]
