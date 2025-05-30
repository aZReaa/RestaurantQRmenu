from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json

from menu.models import Pesanan, DetailPesanan

def user_type_required(user_types):
    """
    Decorator to require specific user types for access
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('authentication:login')
            
            if hasattr(request.user, 'userprofile'):
                if request.user.userprofile.user_type in user_types:
                    return view_func(request, *args, **kwargs)            # If user doesn't have required permissions, redirect to dashboard
            return redirect('authentication:login')
        return _wrapped_view
    return decorator

@login_required
@user_type_required(['DAPUR', 'MANAJER'])
def dapur_index(request):
    """
    Main kitchen dashboard showing orders to be prepared
    """
    # Get orders that need preparation
    pesanan_baru = Pesanan.objects.filter(status='BARU').order_by('created_at')
    pesanan_diproses = Pesanan.objects.filter(status='DIPROSES').order_by('created_at')
    
    context = {
        'pesanan_baru': pesanan_baru,
        'pesanan_diproses': pesanan_diproses,
        'total_baru': pesanan_baru.count(),
        'total_diproses': pesanan_diproses.count(),
    }
    
    return render(request, 'dapur/index.html', context)

@login_required
@user_type_required(['DAPUR', 'MANAJER'])
@csrf_exempt
@require_POST
def update_order_status(request, pesanan_id):
    """
    API endpoint for kitchen staff to update order status
    """
    try:
        pesanan = get_object_or_404(Pesanan, id=pesanan_id)
        
        # Parse data from request
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Kitchen can only change status from BARU to DIPROSES to SELESAI
        valid_transitions = {
            'BARU': ['DIPROSES'],
            'DIPROSES': ['SELESAI'],
            'SELESAI': []  # Cannot change from SELESAI in kitchen
        }
        
        if pesanan.status not in valid_transitions:
            return JsonResponse({
                'status': 'error', 
                'message': 'Status pesanan tidak dapat diubah'
            }, status=400)
        
        if new_status not in valid_transitions[pesanan.status]:
            return JsonResponse({
                'status': 'error', 
                'message': f'Tidak dapat mengubah status dari {pesanan.status} ke {new_status}'
            }, status=400)
        
        # Update status
        old_status = pesanan.status
        pesanan.status = new_status
        pesanan.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Status pesanan berhasil diubah dari {old_status} ke {new_status}',
            'old_status': old_status,
            'new_status': new_status
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@user_type_required(['DAPUR', 'MANAJER'])
def order_detail(request, pesanan_id):
    """
    Show detailed view of a specific order for kitchen staff
    """
    pesanan = get_object_or_404(Pesanan, id=pesanan_id)
    detail_pesanan = pesanan.detailpesanan_set.all()
    
    context = {
        'pesanan': pesanan,
        'detail_pesanan': detail_pesanan,
        'can_update': pesanan.status in ['BARU', 'DIPROSES'],
    }
    
    return render(request, 'dapur/order_detail.html', context)
