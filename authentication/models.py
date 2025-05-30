from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    USER_TYPES = [
        ('SUPERADMIN', 'Super Admin'),
        ('KASIR', 'Kasir'),
        ('DAPUR', 'Dapur'),
        ('MANAJER', 'Manajer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=15, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profile Pengguna"
        verbose_name_plural = "Profile Pengguna"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
    
    @property
    def is_superadmin(self):
        return self.user_type == 'SUPERADMIN'
    
    @property
    def is_kasir(self):
        return self.user_type == 'KASIR'
    
    @property
    def is_dapur(self):
        return self.user_type == 'DAPUR'
    
    @property
    def is_manajer(self):
        return self.user_type == 'MANAJER'
