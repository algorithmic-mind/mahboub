"""
purchase/models.py
خرید تکی بدون سبد خرید — یکپارچه با زرین‌پال
"""
import uuid
from django.db import models
from django.conf import settings


def _ref():
    return uuid.uuid4().hex[:16].upper()


class Purchase(models.Model):
    """هر سطر = یک خرید موفق یا در‌حال‌انجام"""

    class ContentType(models.TextChoices):
        BOOK    = 'book',    'کتاب'
        PODCAST = 'podcast', 'پادکست'
        COURSE  = 'course',  'دوره ویدیویی'

    class Status(models.TextChoices):
        PENDING  = 'pending',  'در انتظار پرداخت'
        SUCCESS  = 'success',  'موفق'
        FAILED   = 'failed',   'ناموفق'
        REFUNDED = 'refunded', 'بازگشت وجه'

    # ── کاربر ─────────────────────────────────────────────────────────────
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='purchases',
        verbose_name='کاربر'
    )

    # ── نوع و شناسه محتوا ─────────────────────────────────────────────────
    content_type = models.CharField(
        max_length=10, choices=ContentType.choices,
        verbose_name='نوع محتوا'
    )
    object_id = models.PositiveIntegerField(verbose_name='شناسه محتوا')

    # ── مالی ──────────────────────────────────────────────────────────────
    amount     = models.PositiveIntegerField(verbose_name='مبلغ (تومان)')
    ref_id     = models.CharField(max_length=32, unique=True, default=_ref, verbose_name='شماره سفارش')
    authority  = models.CharField(max_length=64, blank=True, verbose_name='Authority زرین‌پال')
    zp_ref_id  = models.CharField(max_length=64, blank=True, verbose_name='RefID زرین‌پال (نهایی)')
    status     = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, verbose_name='وضعیت')

    # ── زمان ──────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = 'خرید'
        verbose_name_plural = 'خریدها'
        ordering            = ['-created_at']
        indexes             = [
            models.Index(fields=['user', 'content_type', 'object_id']),
            models.Index(fields=['authority']),
        ]

    def __str__(self):
        return f"#{self.ref_id} — {self.get_content_type_display()} {self.object_id} — {self.get_status_display()}"

    # ── helpers ───────────────────────────────────────────────────────────
    @property
    def is_paid(self):
        return self.status == self.Status.SUCCESS

    @classmethod
    def has_access(cls, user, content_type: str, object_id: int) -> bool:
        """آیا کاربر به این محتوا دسترسی دارد؟"""
        if not user or not user.is_authenticated:
            return False
        return cls.objects.filter(
            user=user,
            content_type=content_type,
            object_id=object_id,
            status=cls.Status.SUCCESS
        ).exists()