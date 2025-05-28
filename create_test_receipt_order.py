from django.utils import timezone
from menu.models import Meja, Pesanan, DetailPesanan, MenuItem

# Create a paid order for testing the receipt feature
def create_test_paid_order():
    # Get a table
    try:
        meja = Meja.objects.get(nomor_meja='1')
    except Meja.DoesNotExist:
        print("Meja tidak ditemukan! Membuat meja baru...")
        meja = Meja.objects.create(nomor_meja='1')
    
    # Create a new order with DIBAYAR status
    pesanan = Pesanan.objects.create(
        meja=meja,
        status='DIBAYAR',
        created_at=timezone.now(),
        analytics_processed=True  # Mark as processed for analytics
    )
    
    # Get some menu items
    try:
        menu_items = MenuItem.objects.all()[:3]  # Get first 3 menu items
        
        if not menu_items:
            print("Tidak ada menu item! Silakan buat menu item terlebih dahulu.")
            return None
            
        # Add menu items to order
        for i, item in enumerate(menu_items):
            jumlah = i + 1  # 1, 2, 3 items respectively
            harga_per_item = item.harga
            subtotal = harga_per_item * jumlah
            
            DetailPesanan.objects.create(
                pesanan=pesanan,
                menu_item=item,
                jumlah=jumlah,
                harga_per_item=harga_per_item,
                subtotal=subtotal
            )
            
        print(f"Pesanan test berhasil dibuat dengan ID: {pesanan.id}")
        print(f"Silakan kunjungi: http://127.0.0.1:8000/kasir/print-receipt/{pesanan.id}/")
        return pesanan
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    create_test_paid_order()
