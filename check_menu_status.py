#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_qr.settings')
django.setup()

from menu.models import MenuItem, KategoriMenu, Meja

print("=== DATABASE STATUS CHECK ===\n")

print("1. MEJA (TABLES):")
mejas = Meja.objects.all()
for meja in mejas:
    print(f"   - {meja.nomor_meja}: aktif={meja.is_aktif}")

print(f"\nTotal Meja: {mejas.count()}")

print("\n2. KATEGORI MENU:")
kategoris = KategoriMenu.objects.all()
for kategori in kategoris:
    print(f"   - {kategori.nama}")

print(f"\nTotal Kategori: {kategoris.count()}")

print("\n3. MENU ITEMS:")
items = MenuItem.objects.all()
for item in items:
    print(f"   - {item.nama}: tersedia={item.is_tersedia}, harga=Rp{item.harga:,.0f}")

print(f"\nTotal Menu Items: {items.count()}")
print(f"Items Tersedia: {items.filter(is_tersedia=True).count()}")
print(f"Items Habis: {items.filter(is_tersedia=False).count()}")

if items.filter(is_tersedia=False).exists():
    print("\n4. ITEMS YANG HABIS:")
    for item in items.filter(is_tersedia=False):
        print(f"   - {item.nama}")
