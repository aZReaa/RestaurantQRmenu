#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_qr.settings')
django.setup()

from menu.models import MenuItem

print("Available menu items:")
for item in MenuItem.objects.all():
    print(f"- {item.nama}")
