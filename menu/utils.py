import qrcode
from io import BytesIO
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def generate_qr_code_for_table(nomor_meja, request=None):
    """
    Generate QR Code untuk meja tertentu
    
    Args:
        nomor_meja: Nomor meja
        request: Django request object untuk mendapatkan domain
    
    Returns:
        Relative path ke file QR Code yang telah disimpan
    """
    # Tentukan base URL
    if request:
        base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
    else:
        base_url = "http://127.0.0.1:8000"  # Default untuk development
    
    # URL menu untuk meja
    menu_url = f"{base_url}/menu/meja/{nomor_meja}/"
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(menu_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Save to media directory
    qr_filename = f"qrcodes/meja_{nomor_meja}.png"
    
    # Ensure directory exists
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Save file
    file_content = ContentFile(buffer.getvalue())
    file_path = default_storage.save(qr_filename, file_content)
    
    return file_path

def generate_all_table_qr_codes(request=None):
    """
    Generate QR Code untuk semua meja yang aktif
    
    Returns:
        Dict dengan nomor meja sebagai key dan path file sebagai value
    """
    from menu.models import Meja
    
    results = {}
    meja_list = Meja.objects.filter(is_aktif=True)
    
    for meja in meja_list:
        try:
            file_path = generate_qr_code_for_table(meja.nomor_meja, request)
            results[meja.nomor_meja] = file_path
        except Exception as e:
            results[meja.nomor_meja] = f"Error: {str(e)}"
    
    return results
