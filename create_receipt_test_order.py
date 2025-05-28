#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_qr.settings')
django.setup()

from menu.models import Meja, MenuItem, Pesanan, DetailPesanan

def create_receipt_test_order():
    """
    Create a test order with DIBAYAR status for testing receipt functionality
    """
    try:
        # Get a table and menu items
        meja = Meja.objects.first()
        if not meja:
            print("No tables found. Please run populate_sample_data.py first.")
            return
            
        menu_items = MenuItem.objects.all()[:3]  # Get first 3 menu items
        if not menu_items:
            print("No menu items found. Please run populate_sample_data.py first.")
            return
            
        # Create a new order
        pesanan = Pesanan.objects.create(
            meja=meja,
            status='DIBAYAR',  # Set as paid so we can test receipt
            total_harga=Decimal('0.00')
        )
        
        print(f"Created order #{pesanan.id} for table {meja.nomor_meja}")
        
        # Add order details
        total = Decimal('0.00')
        for i, menu_item in enumerate(menu_items, 1):
            jumlah = i  # 1, 2, 3 items respectively
            subtotal = menu_item.harga * jumlah
            
            DetailPesanan.objects.create(
                pesanan=pesanan,
                menu_item=menu_item,
                jumlah=jumlah,
                harga_per_item=menu_item.harga,
                subtotal=subtotal
            )
            
            total += subtotal
            print(f"Added {jumlah}x {menu_item.nama} @ Rp{menu_item.harga:,.0f} = Rp{subtotal:,.0f}")
        
        # Update total
        pesanan.total_harga = total
        pesanan.save()
        
        print(f"\nOrder completed! Total: Rp{total:,.0f}")
        print(f"Order ID: {pesanan.id}")
        print(f"Test receipt URL: http://127.0.0.1:8000/kasir/print-receipt/{pesanan.id}/")
        print(f"View table orders: http://127.0.0.1:8000/kasir/kasir_meja/{meja.nomor_meja}/")
        
        return pesanan.id
        
    except Exception as e:
        print(f"Error creating test order: {e}")
        return None

if __name__ == "__main__":
    create_receipt_test_order()
