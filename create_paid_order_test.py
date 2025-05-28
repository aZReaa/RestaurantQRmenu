#!/usr/bin/env python
"""
Script to create a test order with DIBAYAR status for testing receipt functionality
"""
import os
import sys
import django
from datetime import datetime
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_qr.settings')
django.setup()

from menu.models import Meja, MenuItem, Pesanan, DetailPesanan

def create_paid_order():
    try:
        # Get table 1
        meja = Meja.objects.get(nomor_meja='1')
        
        # Get some menu items
        nasi_gudeg = MenuItem.objects.get(nama='Nasi Gudeg')
        es_teh = MenuItem.objects.get(nama='Es Teh Manis')
        kerupuk = MenuItem.objects.get(nama='Kerupuk')
        
        # Create order with DIBAYAR status
        pesanan = Pesanan.objects.create(
            meja=meja,
            status='DIBAYAR',
            total_harga=Decimal('0')  # Will be calculated below
        )
        
        # Create order details
        detail1 = DetailPesanan.objects.create(
            pesanan=pesanan,
            menu_item=nasi_gudeg,
            jumlah=2,
            harga_per_item=nasi_gudeg.harga,
            subtotal=nasi_gudeg.harga * 2
        )
        
        detail2 = DetailPesanan.objects.create(
            pesanan=pesanan,
            menu_item=es_teh,
            jumlah=2,
            harga_per_item=es_teh.harga,
            subtotal=es_teh.harga * 2
        )
        
        detail3 = DetailPesanan.objects.create(
            pesanan=pesanan,
            menu_item=kerupuk,
            jumlah=1,
            harga_per_item=kerupuk.harga,
            subtotal=kerupuk.harga * 1
        )
        
        # Calculate and update total
        total = detail1.subtotal + detail2.subtotal + detail3.subtotal
        pesanan.total_harga = total
        pesanan.save()
        
        print(f"✅ Created paid order #{pesanan.id} for table {meja.nomor_meja}")
        print(f"   Items: {detail1.jumlah}x {nasi_gudeg.nama}, {detail2.jumlah}x {es_teh.nama}, {detail3.jumlah}x {kerupuk.nama}")
        print(f"   Total: Rp {total:,.0f}")
        print(f"   Status: {pesanan.get_status_display()}")
        print(f"   Receipt URL: http://127.0.0.1:8000/kasir/print-receipt/{pesanan.id}/")
        
        return pesanan
        
    except Exception as e:
        print(f"❌ Error creating paid order: {e}")
        return None

if __name__ == "__main__":
    print("Creating test paid order...")
    create_paid_order()
