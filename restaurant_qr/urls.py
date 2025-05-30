"""
URL configuration for restaurant_qr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    """
    Home view that redirects based on user role
    """
    # Import here to avoid circular imports
    from authentication.views import redirect_by_role
    return redirect_by_role(request.user)

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('menu/', include('menu.urls')),
    path('kasir/', include('kasir.urls')),
    path('dapur/', include('dapur.urls')),
    path('auth/', include('authentication.urls', namespace='authentication')),
]

# Serving media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
