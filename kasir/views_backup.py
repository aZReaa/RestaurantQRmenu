from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import models
from django.core.paginator import Paginator
from django.db.models import Q
import json

from menu.models import Meja, Pesanan, DetailPesanan

def user_type_required(user_types):
    """
    Decorator to require specific user types for access
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('authentication:login')
            
            # Allow superuser access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if hasattr(request.user, 'userprofile'):
                if request.user.userprofile.user_type in user_types:
                    return view_func(request, *args, **kwargs)
            
            # Redirect to appropriate dashboard based on user type
            from authentication.views import redirect_by_role
            return redirect_by_role(request.user)
        return _wrapped_view
    return decorator

@login_required
@user_type_required(['KASIR'])
def kasir_index(request):
    """
    Main kasir dashboard with search and pagination
    """
    # Search functionality
    search_query = request.GET.get('search', '')
    search_type = request.GET.get('search_type', 'all')
    
    # Base queries
    pesanan_siap_bayar = Pesanan.objects.filter(status='SELESAI').select_related('meja').prefetch_related('detailpesanan_set__menu_item')
    pesanan_diproses = Pesanan.objects.filter(status__in=['BARU', 'DIPROSES']).select_related('meja')
    
    # Apply search filters
    if search_query:
        if search_type == 'meja':
            pesanan_siap_bayar = pesanan_siap_bayar.filter(meja__nomor_meja__icontains=search_query)
            pesanan_diproses = pesanan_diproses.filter(meja__nomor_meja__icontains=search_query)
        elif search_type == 'id':
            pesanan_siap_bayar = pesanan_siap_bayar.filter(id__icontains=search_query)
            pesanan_diproses = pesanan_diproses.filter(id__icontains=search_query)
        else:  # 'all'
            pesanan_siap_bayar = pesanan_siap_bayar.filter(
                Q(meja__nomor_meja__icontains=search_query) | 
                Q(id__icontains=search_query) |
                Q(nama_pemesan__icontains=search_query)
            )
            pesanan_diproses = pesanan_diproses.filter(
                Q(meja__nomor_meja__icontains=search_query) | 
                Q(id__icontains=search_query) |
                Q(nama_pemesan__icontains=search_query)
            )
    
    # Order by creation time
    pesanan_siap_bayar = pesanan_siap_bayar.order_by('created_at')
    pesanan_diproses = pesanan_diproses.order_by('created_at')
    
    # Pagination for orders ready for payment
    siap_bayar_paginator = Paginator(pesanan_siap_bayar, 10)  # 10 orders per page
    siap_bayar_page = request.GET.get('siap_page')
    pesanan_siap_bayar_page = siap_bayar_paginator.get_page(siap_bayar_page)
      # Pagination for orders in progress (limited display)
    diproses_paginator = Paginator(pesanan_diproses, 5)  # 5 orders per page for in-progress
    diproses_page = request.GET.get('diproses_page')
    pesanan_diproses_page = diproses_paginator.get_page(diproses_page)
    
    # Statistics
    total_siap_bayar = pesanan_siap_bayar.count()
    total_diproses = pesanan_diproses.count()
    total_pendapatan_hari_ini = Pesanan.objects.filter(
        status='DIBAYAR',
        created_at__date=timezone.now().date()
    ).aggregate(total=models.Sum('total_harga'))['total'] or 0
    
    context = {
        'pesanan_siap_bayar': pesanan_siap_bayar_page,
        'pesanan_diproses': pesanan_diproses_page,
        'total_siap_bayar': total_siap_bayar,
        'total_diproses': total_diproses,
        'total_pendapatan_hari_ini': total_pendapatan_hari_ini,
        'search_query': search_query,
        'search_type': search_type,
        'kasir_name': request.user.get_full_name() or request.user.username,
    }
    
    return render(request, 'kasir/kasir_improved.html', context)

@login_required
@user_type_required(['KASIR', 'MANAJER'])
def detail_pesanan_meja(request, nomor_meja):
    """
    View untuk menampilkan detail pesanan berdasarkan meja
    """
    # Ambil meja
    meja = get_object_or_404(Meja, nomor_meja=nomor_meja)
    
    # Ambil pesanan yang belum dibayar untuk meja tersebut
    pesanan_list = Pesanan.objects.filter(
        meja=meja,
        status__in=['BARU', 'DIPROSES', 'SELESAI']
    ).order_by('-created_at')
    
    context = {
        'meja': meja,
        'pesanan_list': pesanan_list,
    }
    
    return render(request, 'kasir/detail_pesanan_meja.html', context)

@login_required
@user_type_required(['KASIR', 'DAPUR', 'MANAJER'])
@csrf_exempt
@require_POST
def update_status_pesanan(request, pesanan_id):
    """
    API endpoint untuk update status pesanan
    """
    try:
        # Ambil pesanan
        pesanan = get_object_or_404(Pesanan, id=pesanan_id)
        
        # Parse data dari request
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Validasi status
        valid_statuses = ['BARU', 'DIPROSES', 'SELESAI', 'DIBAYAR', 'DIBATALKAN']
        if new_status not in valid_statuses:
            return JsonResponse({'status': 'error', 'message': 'Status tidak valid'}, status=400)
        
        # Update status
        pesanan.status = new_status
        pesanan.save()
        
        return JsonResponse({'status': 'success', 'message': 'Status pesanan berhasil diupdate'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@user_type_required(['KASIR', 'MANAJER'])
def print_receipt(request, pesanan_id):
    """
    View untuk print receipt pesanan
    """
    pesanan = get_object_or_404(Pesanan, id=pesanan_id)
    
    # Hitung total pesanan
    detail_pesanan = pesanan.detailpesanan_set.all()
    subtotal = sum(detail.subtotal for detail in detail_pesanan)
      # Hitung pajak dan total
    from decimal import Decimal
    tax_rate = Decimal('0.1')  # 10% tax
    tax_amount = subtotal * tax_rate
    grand_total = subtotal + tax_amount
      context = {
        'pesanan': pesanan,
        'detail_pesanan': detail_pesanan,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'grand_total': grand_total,
        'print_time': timezone.now(),
        'kasir_name': request.user.get_full_name() or request.user.username,
    }
    
    # Render template khusus untuk receipt
    receipt_html = render_to_string('kasir/receipt.html', context)
    
    # Return sebagai response HTML yang bisa di-print
    response = HttpResponse(receipt_html, content_type='text/html')
    response['Content-Disposition'] = f'inline; filename="receipt_pesanan_{pesanan_id}.html"'
    
    return response

@login_required
@user_type_required(['KASIR'])
def process_payment(request, pesanan_id):
    """
    Process payment for an order
    """
    pesanan = get_object_or_404(Pesanan, id=pesanan_id)
    
    # Verify order is ready for payment
    if pesanan.status != 'SELESAI':
        from django.contrib import messages
        messages.error(request, 'Pesanan belum siap untuk dibayar.')
        return redirect('kasir:kasir_index')
    
    if request.method == 'POST':
        # Process payment
        pesanan.status = 'DIBAYAR'
        pesanan.waktu_pembayaran = timezone.now()
        pesanan.save()
        
        from django.contrib import messages
        messages.success(request, f'Pembayaran pesanan #{pesanan.id} berhasil diproses.')
        return redirect('kasir:print_receipt', pesanan_id=pesanan.id)
    
    # Calculate order details
    detail_pesanan = pesanan.detailpesanan_set.all()
    subtotal = sum(detail.subtotal for detail in detail_pesanan)
    
    # Calculate tax and total
    from decimal import Decimal
    tax_rate = Decimal('0.1')  # 10% tax
    tax_amount = subtotal * tax_rate
    grand_total = subtotal + tax_amount
    
    context = {
        'pesanan': pesanan,
        'detail_pesanan': detail_pesanan,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'grand_total': grand_total,
    }
    
    return render(request, 'kasir/process_payment.html', context)
