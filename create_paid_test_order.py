#!/usr/bin/env python3

import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_qr.settings')
django.setup()

from menu.models import Meja, MenuItem, Pesanan, DetailPesanan

def create_paid_test_order():
    """Create a test order with DIBAYAR status for receipt testing"""
    
    try:
        # Get table 1
        meja = Meja.objects.get(nomor_meja='1')
        
        # Get some menu items
        menu_items = MenuItem.objects.all()[:3]  # Get first 3 menu items
        
        if not menu_items:
            print("No menu items found! Please run populate_sample_data.py first")
            return
        
        # Create order with DIBAYAR status
        pesanan = Pesanan.objects.create(
            meja=meja,
            status='DIBAYAR'
        )
        
        total_amount = Decimal('0')
        
        # Add menu items to order
        for i, menu_item in enumerate(menu_items, 1):
            quantity = i  # Different quantities for variety
            subtotal = menu_item.harga * quantity
            total_amount += subtotal
            
            DetailPesanan.objects.create(
                pesanan=pesanan,
                menu_item=menu_item,
                jumlah=quantity,
                harga_per_item=menu_item.harga,
                subtotal=subtotal
            )
        
        print(f"✅ Created paid test order:")
        print(f"   Order ID: {pesanan.id}")
        print(f"   Table: {meja.nomor_meja}")
        print(f"   Status: {pesanan.get_status_display()}")
        print(f"   Total Items: {pesanan.detailpesanan_set.count()}")
        print(f"   Total Amount: Rp {total_amount:,.0f}")
        print(f"   Receipt URL: http://127.0.0.1:8000/kasir/print-receipt/{pesanan.id}/")
        
        return pesanan
        
    except Exception as e:
        print(f"❌ Error creating test order: {e}")
        return None

if __name__ == "__main__":
    create_paid_test_order()
