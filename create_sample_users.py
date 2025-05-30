#!/usr/bin/env python
"""
Script to create sample users for testing the authentication system.
Run this script to create test users for different user types.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_qr.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

def create_sample_users():
    """Create sample users for testing different user types."""
    
    # Sample user data
    users_data = [
        {
            'username': 'kasir1',
            'password': 'kasir123',
            'first_name': 'Ahmad',
            'last_name': 'Kasir',
            'email': 'kasir1@restaurant.com',
            'user_type': 'KASIR'
        },
        {
            'username': 'kasir2',
            'password': 'kasir123',
            'first_name': 'Siti',
            'last_name': 'Kasir',
            'email': 'kasir2@restaurant.com',
            'user_type': 'KASIR'
        },
        {
            'username': 'dapur1',
            'password': 'dapur123',
            'first_name': 'Budi',
            'last_name': 'Chef',
            'email': 'dapur1@restaurant.com',
            'user_type': 'DAPUR'
        },
        {
            'username': 'dapur2',
            'password': 'dapur123',
            'first_name': 'Rina',
            'last_name': 'Cook',
            'email': 'dapur2@restaurant.com',
            'user_type': 'DAPUR'
        },
        {
            'username': 'manajer1',
            'password': 'manajer123',
            'first_name': 'Pak',
            'last_name': 'Manager',
            'email': 'manajer1@restaurant.com',
            'user_type': 'MANAJER'
        },
        {
            'username': 'admin',
            'password': 'admin123',
            'first_name': 'Super',
            'last_name': 'Admin',
            'email': 'admin@restaurant.com',
            'user_type': 'MANAJER',
            'is_superuser': True,
            'is_staff': True
        }
    ]
    
    print("Creating sample users...")
    print("=" * 50)
    
    for user_data in users_data:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"❌ User '{username}' already exists, skipping...")
            continue
        
        # Create user
        user = User.objects.create_user(
            username=username,
            password=user_data['password'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        
        # Set admin privileges if specified
        if user_data.get('is_superuser'):
            user.is_superuser = True
        if user_data.get('is_staff'):
            user.is_staff = True
        user.save()
        
        # Create UserProfile
        UserProfile.objects.create(
            user=user,
            user_type=user_data['user_type']
        )
        
        print(f"✅ Created user: {username} ({user_data['user_type']}) - {user_data['first_name']} {user_data['last_name']}")
    
    print("=" * 50)
    print("Sample users created successfully!")
    print("\nLogin credentials:")
    print("=" * 30)
    
    for user_data in users_data:
        print(f"👤 {user_data['user_type']}: {user_data['username']} / {user_data['password']}")
    
    print("\n🌐 You can now test the authentication system at:")
    print("   http://127.0.0.1:8000/auth/login/")

if __name__ == '__main__':
    create_sample_users()
