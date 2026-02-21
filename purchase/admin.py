from django.contrib import admin
from django.utils.html import format_html
from .models import Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display  = ('ref_id', 'user', 'content_type', 'object_id', 'amount_display', 'status_badge', 'created_at', 'paid_at')
    list_filter   = ('status', 'content_type', 'created_at')
    search_fields = ('ref_id', 'user__phone_number', 'authority', 'zp_ref_id')
    readonly_fields = ('ref_id', 'authority', 'zp_ref_id', 'created_at', 'paid_at')
    ordering      = ('-created_at',)
    date_hierarchy= 'created_at'

    def amount_display(self, obj):
        return f'{obj.amount:,} تومان'
    amount_display.short_description = 'مبلغ'

    def status_badge(self, obj):
        colors = {
            'pending':  ('#fd7e14', '#fff3cd'),
            'success':  ('#198754', '#d1e7dd'),
            'failed':   ('#dc3545', '#f8d7da'),
            'refunded': ('#6c757d', '#e2e3e5'),
        }
        color, bg = colors.get(obj.status, ('#555', '#eee'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:12px;font-size:11px;font-weight:bold;">{}</span>',
            bg, color, obj.get_status_display()
        )
    status_badge.short_description = 'وضعیت'