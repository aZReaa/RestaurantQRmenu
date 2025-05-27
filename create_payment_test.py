#!/usr/bin/env python
"""
Script untuk membuat test order baru untuk testing payment
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_qr.settings')
django.setup()

from menu.models import Meja, MenuItem, Pesanan, DetailPesanan

def create_payment_test_order():
    """
    Membuat test order untuk testing payment functionality
    """
    print("🍽️  Membuat test order untuk payment...")
    
    # Ambil data yang dibutuhkan
    meja_4 = Meja.objects.get(nomor_meja='4')
    
    # Ambil beberapa menu items
    nasi_gudeg = MenuItem.objects.get(nama='Nasi Gudeg Jogja')
    es_teh = MenuItem.objects.get(nama='Es Teh Manis')
    
    # Order 4 - Meja 4 (Status: SELESAI) - siap untuk dibayar
    pesanan4 = Pesanan.objects.create(
        meja=meja_4,
        status='SELESAI',
        catatan='Test order untuk payment',
        analytics_processed=False,  # Belum diproses analytics
        created_at=timezone.now() - timedelta(minutes=10)
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan4,
        menu_item=nasi_gudeg,
        jumlah=1,
        harga_per_item=nasi_gudeg.harga,
        subtotal=1 * nasi_gudeg.harga
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan4,
        menu_item=es_teh,
        jumlah=2,
        harga_per_item=es_teh.harga,
        subtotal=2 * es_teh.harga
    )
    
    # Hitung total
    pesanan4.total_harga = sum(detail.subtotal for detail in pesanan4.detailpesanan_set.all())
    pesanan4.save()
    
    print(f"✅ Test order dibuat: Pesanan #{pesanan4.id} - Meja {meja_4.nomor_meja} (Status: SELESAI)")
    print(f"💰 Total: Rp {pesanan4.total_harga}")
    print(f"🔄 Analytics processed: {pesanan4.analytics_processed}")
    print("\n🎯 Silakan test payment di: http://127.0.0.1:8000/kasir/kasir_meja/4/")

if __name__ == '__main__':
    create_payment_test_order()
