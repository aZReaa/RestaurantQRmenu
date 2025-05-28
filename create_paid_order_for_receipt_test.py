#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_qr.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from menu.models import Meja, MenuItem, Pesanan, DetailPesanan

def create_paid_order():
    try:
        # Get table 1
        meja = Meja.objects.get(nomor_meja=1)
        
        # Get some menu items
        nasi_gudeg = MenuItem.objects.get(nama='Nasi Gudeg')
        es_jeruk = MenuItem.objects.get(nama='Es Jeruk')
        
        # Create a paid order
        pesanan = Pesanan.objects.create(
            meja=meja,
            status='DIBAYAR',
            analytics_processed=False
        )
        
        # Add order details
        DetailPesanan.objects.create(
            pesanan=pesanan,
            menu_item=nasi_gudeg,
            jumlah=2,
            harga_per_item=nasi_gudeg.harga,
            subtotal=nasi_gudeg.harga * 2
        )
        
        DetailPesanan.objects.create(
            pesanan=pesanan,
            menu_item=es_jeruk,
            jumlah=1,
            harga_per_item=es_jeruk.harga,
            subtotal=es_jeruk.harga * 1
        )
        
        print(f"Created paid order #{pesanan.id} for Table {meja.nomor_meja}")
        print(f"Status: {pesanan.get_status_display()}")
        
        # Calculate totals
        details = pesanan.detailpesanan_set.all()
        subtotal = sum(detail.subtotal for detail in details)
        tax_amount = subtotal * 0.1
        grand_total = subtotal + tax_amount
        
        print(f"Subtotal: Rp {subtotal:,.0f}")
        print(f"Tax (10%): Rp {tax_amount:,.0f}")
        print(f"Grand Total: Rp {grand_total:,.0f}")
        print(f"\nOrder details:")
        for detail in details:
            print(f"- {detail.menu_item.nama} x{detail.jumlah} @ Rp {detail.harga_per_item:,.0f} = Rp {detail.subtotal:,.0f}")
        
        print(f"\nReceipt URL: http://127.0.0.1:8000/kasir/print-receipt/{pesanan.id}/")
        return pesanan.id
        
    except Exception as e:
        print(f"Error creating paid order: {e}")
        return None

if __name__ == '__main__':
    create_paid_order()
