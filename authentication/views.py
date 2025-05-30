from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from .models import UserProfile
import json


def login_view(request):
    """
    View untuk halaman login
    """
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Check if user profile exists and is active
                    try:
                        profile = UserProfile.objects.get(user=user)
                        if not profile.is_active:
                            logout(request)
                            messages.error(request, 'Akun Anda telah dinonaktifkan. Hubungi administrator.')
                            return render(request, 'authentication/login.html')
                    except UserProfile.DoesNotExist:
                        # For superuser/admin without profile
                        if user.is_superuser:
                            messages.success(request, f'Selamat datang, Super Admin {user.first_name or user.username}!')
                            return redirect('authentication:admin_dashboard')
                        else:
                            logout(request)
                            messages.error(request, 'Profile pengguna tidak ditemukan. Hubungi administrator.')
                            return render(request, 'authentication/login.html')
                    
                    messages.success(request, f'Selamat datang, {user.first_name or user.username}!')
                    return redirect_by_role(user)
                else:
                    messages.error(request, 'Akun Anda telah dinonaktifkan.')
            else:
                messages.error(request, 'Username atau password tidak valid.')
        else:
            messages.error(request, 'Harap isi username dan password.')
    
    return render(request, 'authentication/login.html')


def redirect_by_role(user):
    """
    Redirect user based on their role
    """
    # Check if superuser
    if user.is_superuser:
        return redirect('authentication:admin_dashboard')
    
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.is_superadmin:
            return redirect('authentication:admin_dashboard')
        elif profile.is_kasir:
            return redirect('kasir:kasir_index')
        elif profile.is_dapur:
            return redirect('dapur:index')
        elif profile.is_manajer:
            return redirect('menu:analytics')
    except UserProfile.DoesNotExist:
        return redirect('authentication:login')
    
    return redirect('authentication:login')


@login_required
def logout_view(request):
    """
    View untuk logout
    """
    logout(request)
    messages.success(request, 'Anda telah berhasil logout.')
    return redirect('authentication:login')


@login_required
def user_dashboard(request):
    """
    Dashboard untuk redirect otomatis berdasarkan user type
    """
    return redirect_by_role(request.user)


def superadmin_required(view_func):
    """
    Decorator untuk memastikan hanya superadmin yang dapat mengakses
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentication:login')
        
        # Check if superuser or superadmin
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.is_superadmin:
                return view_func(request, *args, **kwargs)
        except UserProfile.DoesNotExist:
            pass
        
        messages.error(request, 'Akses ditolak. Hanya Super Admin yang dapat mengakses halaman ini.')
        return redirect_by_role(request.user)
    
    return _wrapped_view


@login_required
@superadmin_required
def admin_dashboard(request):
    """
    Dashboard khusus untuk Super Admin
    """
    # Statistics
    total_users = User.objects.count()
    total_kasir = UserProfile.objects.filter(user_type='KASIR').count()
    total_dapur = UserProfile.objects.filter(user_type='DAPUR').count()
    total_manajer = UserProfile.objects.filter(user_type='MANAJER').count()
    
    # Recent users
    recent_users = UserProfile.objects.select_related('user').order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_kasir': total_kasir,
        'total_dapur': total_dapur,
        'total_manajer': total_manajer,
        'recent_users': recent_users,
    }
    
    return render(request, 'authentication/admin_dashboard.html', context)


@login_required
@superadmin_required
def user_management(request):
    """
    User management for Super Admin
    """
    search_query = request.GET.get('search', '')
    user_type_filter = request.GET.get('user_type', '')
    
    # Base query
    users = UserProfile.objects.select_related('user').all()
    
    # Apply filters
    if search_query:
        users = users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)
    
    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    context = {
        'users': users_page,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
        'user_types': UserProfile.USER_TYPES,
    }
    
    return render(request, 'authentication/user_management.html', context)


@login_required
@superadmin_required
def create_user(request):
    """
    Create new user
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        phone_number = request.POST.get('phone_number')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            
            # Create profile
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone_number=phone_number
            )
            
            messages.success(request, f'User {username} berhasil dibuat.')
            return redirect('authentication:user_management')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'user_types': UserProfile.USER_TYPES,
    }
    
    return render(request, 'authentication/create_user.html', context)


@csrf_exempt
def check_auth_status(request):
    """
    API endpoint untuk check status authentication
    """
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            return JsonResponse({
                'authenticated': True,
                'username': request.user.username,
                'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'user_type': profile.get_user_type_display(),
                'user_type_code': profile.user_type
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'authenticated': True,
                'username': request.user.username,
                'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'user_type': 'Administrator',
                'user_type_code': 'ADMIN'
            })
    
    return JsonResponse({'authenticated': False})


@csrf_exempt
@login_required
@superadmin_required
def toggle_user_status(request):
    """
    AJAX endpoint to toggle user active status
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            is_active = data.get('is_active')
            
            try:
                user_profile = UserProfile.objects.get(id=user_id)
                
                # Don't allow deactivating superuser
                if user_profile.user.is_superuser:
                    return JsonResponse({
                        'success': False,
                        'message': 'Tidak dapat mengubah status superuser'
                    })
                
                user_profile.is_active = is_active
                user_profile.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Status user berhasil {"diaktifkan" if is_active else "dinonaktifkan"}'
                })
            except UserProfile.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'User tidak ditemukan'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})


@csrf_exempt
@login_required
@superadmin_required
def delete_user(request):
    """
    AJAX endpoint to delete user
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            try:
                user_profile = UserProfile.objects.get(id=user_id)
                
                # Don't allow deleting superuser
                if user_profile.user.is_superuser:
                    return JsonResponse({
                        'success': False,
                        'message': 'Tidak dapat menghapus superuser'
                    })
                
                # Don't allow deleting own account
                if user_profile.user == request.user:
                    return JsonResponse({
                        'success': False,
                        'message': 'Tidak dapat menghapus akun sendiri'
                    })
                
                username = user_profile.user.username
                user_profile.user.delete()  # This will also delete the profile due to CASCADE
                
                return JsonResponse({
                    'success': True,
                    'message': f'User {username} berhasil dihapus'
                })
            except UserProfile.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'User tidak ditemukan'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})
