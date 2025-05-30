from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_index, name='menu_index'),
    path('meja/<str:nomor_meja>/', views.menu_view, name='menu_meja'),
    path('api/tambah-ke-keranjang/', views.tambah_ke_keranjang, name='tambah_ke_keranjang'),
    path('api/keranjang/checkout/', views.checkout_keranjang, name='checkout_keranjang'),
    path('qr-codes/', views.generate_qr_codes_view, name='qr_codes'),
    path('qr-codes/download/<str:nomor_meja>/', views.download_qr_code, name='download_qr_code'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
]
