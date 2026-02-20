from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("شماره موبایل الزامی است")
        
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if password is None:
            raise ValueError("سوپریوزر حتماً باید دارای رمز عبور باشد")
            
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=11, 
        unique=True, 
        db_index=True,
        verbose_name="شماره موبایل"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_staff = models.BooleanField(default=False, verbose_name="دسترسی مدیریت")
    
    # تاریخ‌ها
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ عضویت")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="آخرین ورود")
    
    # فیلدهای OTP
    otp_code = models.CharField(max_length=6, blank=True, null=True, verbose_name="کد تایید")
    otp_created_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان ایجاد کد")

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ['-date_joined']

    def __str__(self):
        return self.phone_number

    def is_otp_valid(self, otp_code, expiry_minutes=5):
        """بررسی اعتبار کد OTP"""
        if not self.otp_code or not self.otp_created_at:
            return False
        
        expiry_time = self.otp_created_at + timedelta(minutes=expiry_minutes)
        return self.otp_code == otp_code and timezone.now() <= expiry_time

    def clear_otp(self):
        """پاک کردن کد OTP بعد از استفاده"""
        self.otp_code = None
        self.otp_created_at = None
        self.save(update_fields=['otp_code', 'otp_created_at'])

    def set_otp(self, otp_code):
        """تنظیم کد OTP جدید"""
        self.otp_code = otp_code
        self.otp_created_at = timezone.now()
        self.save(update_fields=['otp_code', 'otp_created_at'])