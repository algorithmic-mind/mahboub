# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import User

class UserAdmin(BaseUserAdmin):
    # فرم نمایش در ادمین
    list_display = ['phone_number', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['phone_number']
    ordering = ['-date_joined']
    
    # فیلدهایی که در صفحه جزئیات نمایش داده می‌شوند
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('OTP Information'), {
            'fields': ('otp_code', 'otp_created_at'),
            'classes': ('collapse',),  # قابل باز و بسته شدن
        }),
    )
    
    # فیلدهای هنگام ایجاد کاربر جدید
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )
    
    # فیلدهای فقط خواندنی
    readonly_fields = ['last_login', 'date_joined']

# ثبت مدل در ادمین
admin.site.register(User, UserAdmin)

# از آنجایی که از مدل سفارشی استفاده می‌کنیم، نیازی به ثبت Group نیست
# اما اگر می‌خواهید Group هم در ادمین بماند:
# admin.site.unregister(Group)