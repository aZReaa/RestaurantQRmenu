from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('toggle-user-status/', views.toggle_user_status, name='toggle_user_status'),
    path('delete-user/', views.delete_user, name='delete_user'),
    path('api/check-auth/', views.check_auth_status, name='check_auth'),
]
