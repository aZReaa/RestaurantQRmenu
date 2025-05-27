#!/usr/bin/env python
"""
Script untuk membuat test orders untuk demonstrasi sistem
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

def create_test_orders():
    """
    Membuat beberapa test orders untuk demonstrasi
    """
    print("🍽️  Membuat test orders...")
    
    # Ambil data yang dibutuhkan
    meja_1 = Meja.objects.get(nomor_meja='1')
    meja_2 = Meja.objects.get(nomor_meja='2')
    meja_3 = Meja.objects.get(nomor_meja='3')
    
    # Ambil beberapa menu items
    nasi_gudeg = MenuItem.objects.get(nama='Nasi Gudeg Jogja')
    ayam_bakar = MenuItem.objects.get(nama='Ayam Bakar Taliwang')
    es_teh = MenuItem.objects.get(nama='Es Teh Manis')
    es_jeruk = MenuItem.objects.get(nama='Es Jeruk')
    kerupuk = MenuItem.objects.get(nama='Kerupuk Udang')
    
    # Order 1 - Meja 1 (Status: BARU)
    pesanan1 = Pesanan.objects.create(
        meja=meja_1,
        status='BARU',
        catatan='Ayam bakarnya extra pedas ya',
        created_at=timezone.now() - timedelta(minutes=5)
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan1,
        menu_item=nasi_gudeg,
        jumlah=2,
        harga_per_item=nasi_gudeg.harga,
        subtotal=2 * nasi_gudeg.harga,
        catatan_item='Level pedas sedang'
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan1,
        menu_item=ayam_bakar,
        jumlah=1,
        harga_per_item=ayam_bakar.harga,
        subtotal=1 * ayam_bakar.harga,
        catatan_item='Extra pedas'
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan1,
        menu_item=es_teh,
        jumlah=2,
        harga_per_item=es_teh.harga,
        subtotal=2 * es_teh.harga
    )
    
    # Hitung total
    pesanan1.total_harga = sum(detail.subtotal for detail in pesanan1.detailpesanan_set.all())
    pesanan1.save()
    
    print(f"✅ Order 1 dibuat: Pesanan #{pesanan1.id} - Meja {meja_1.nomor_meja} (Status: BARU)")
    
    # Order 2 - Meja 2 (Status: DIPROSES)
    pesanan2 = Pesanan.objects.create(
        meja=meja_2,
        status='DIPROSES',
        catatan='Tanpa sambal',
        created_at=timezone.now() - timedelta(minutes=15)
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan2,
        menu_item=nasi_gudeg,
        jumlah=1,
        harga_per_item=nasi_gudeg.harga,
        subtotal=1 * nasi_gudeg.harga,
        catatan_item='Tanpa sambal'
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan2,
        menu_item=kerupuk,
        jumlah=2,
        harga_per_item=kerupuk.harga,
        subtotal=2 * kerupuk.harga
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan2,
        menu_item=es_jeruk,
        jumlah=1,
        harga_per_item=es_jeruk.harga,
        subtotal=1 * es_jeruk.harga
    )
    
    # Hitung total
    pesanan2.total_harga = sum(detail.subtotal for detail in pesanan2.detailpesanan_set.all())
    pesanan2.save()
    
    print(f"✅ Order 2 dibuat: Pesanan #{pesanan2.id} - Meja {meja_2.nomor_meja} (Status: DIPROSES)")
    
    # Order 3 - Meja 3 (Status: SELESAI)
    pesanan3 = Pesanan.objects.create(
        meja=meja_3,
        status='SELESAI',
        created_at=timezone.now() - timedelta(minutes=25)
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan3,
        menu_item=ayam_bakar,
        jumlah=2,
        harga_per_item=ayam_bakar.harga,
        subtotal=2 * ayam_bakar.harga
    )
    
    DetailPesanan.objects.create(
        pesanan=pesanan3,
        menu_item=es_teh,
        jumlah=2,
        harga_per_item=es_teh.harga,
        subtotal=2 * es_teh.harga
    )
    
    # Hitung total
    pesanan3.total_harga = sum(detail.subtotal for detail in pesanan3.detailpesanan_set.all())
    pesanan3.save()
    
    print(f"✅ Order 3 dibuat: Pesanan #{pesanan3.id} - Meja {meja_3.nomor_meja} (Status: SELESAI)")
    
    print("\n🎉 Test orders berhasil dibuat!")
    print(f"📊 Total orders: {Pesanan.objects.count()}")
    print(f"🔥 Orders BARU: {Pesanan.objects.filter(status='BARU').count()}")
    print(f"⏳ Orders DIPROSES: {Pesanan.objects.filter(status='DIPROSES').count()}")
    print(f"✅ Orders SELESAI: {Pesanan.objects.filter(status='SELESAI').count()}")

if __name__ == '__main__':
    create_test_orders()
