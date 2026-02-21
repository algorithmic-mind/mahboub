"""
purchase/views.py
جریان خرید تکی: start → zarinpal → callback
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages

from .models import Purchase
from .zarinpal import request_payment, verify_payment


# ─────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────

def _get_content_object(content_type: str, object_id: int):
    """برگرداندن شیء محتوا بر اساس نوع"""
    if content_type == 'book':
        from book.models import Book
        return get_object_or_404(Book, pk=object_id, is_active=True)
    elif content_type == 'podcast':
        from podcast.models import Podcast
        return get_object_or_404(Podcast, pk=object_id, is_active=True)
    elif content_type == 'course':
        from course.models import Course
        return get_object_or_404(Course, pk=object_id, is_active=True)
    return None


def _content_redirect(content_type: str, obj) -> str:
    """آدرس بعد از خرید موفق"""
    if content_type == 'book':
        return reverse('books:book_detail', kwargs={'slug': obj.slug})
    elif content_type == 'podcast':
        return reverse('podcasts:podcast_detail', kwargs={'slug': obj.slug})
    elif content_type == 'course':
        return reverse('courses:course_detail', kwargs={'slug': obj.slug})
    return '/'


# ─────────────────────────────────────────────────────────────────────────
# start purchase
# ─────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def start_purchase(request, content_type, object_id):
    """
    POST /purchase/start/<content_type>/<object_id>/
    ایجاد رکورد Purchase و redirect به درگاه
    """
    if content_type not in ('book', 'podcast', 'course'):
        messages.error(request, 'نوع محتوای نامعتبر')
        return redirect('/')

    obj = _get_content_object(content_type, object_id)

    # بررسی دسترسی قبلی
    if Purchase.has_access(request.user, content_type, object_id):
        messages.info(request, 'شما قبلاً این محتوا را خریداری کرده‌اید.')
        return redirect(_content_redirect(content_type, obj))

    # قیمت
    if content_type == 'book':
        amount = obj.final_price
        desc   = f'خرید کتاب: {obj.title}'
    elif content_type == 'podcast':
        amount = obj.final_price
        desc   = f'خرید پادکست: {obj.title}'
    else:
        amount = obj.final_price
        desc   = f'خرید دوره: {obj.title}'

    if amount == 0:
        messages.info(request, 'این محتوا رایگان است.')
        return redirect(_content_redirect(content_type, obj))

    # ساخت رکورد خرید
    purchase = Purchase.objects.create(
        user         = request.user,
        content_type = content_type,
        object_id    = object_id,
        amount       = amount,
    )

    callback_url = request.build_absolute_uri(
        reverse('purchase:callback', kwargs={'ref_id': purchase.ref_id})
    )

    result = request_payment(
        amount_toman = amount,
        description  = desc,
        callback_url = callback_url,
        mobile       = request.user.phone_number,
    )

    if result['ok']:
        purchase.authority = result['authority']
        purchase.save(update_fields=['authority'])
        return redirect(result['gateway_url'])
    else:
        purchase.status = Purchase.Status.FAILED
        purchase.save(update_fields=['status'])
        messages.error(request, f'خطا در اتصال به درگاه: {result["error"]}')
        return redirect(_content_redirect(content_type, obj))


# ─────────────────────────────────────────────────────────────────────────
# callback
# ─────────────────────────────────────────────────────────────────────────

def payment_callback(request, ref_id):
    """
    GET /purchase/callback/<ref_id>/
    زرین‌پال کاربر را اینجا باز می‌گرداند
    """
    purchase = get_object_or_404(Purchase, ref_id=ref_id)
    status   = request.GET.get('Status', '')
    authority= request.GET.get('Authority', '')

    if status != 'OK':
        purchase.status = Purchase.Status.FAILED
        purchase.save(update_fields=['status'])
        return render(request, 'purchase/result.html', {
            'success': False,
            'message': 'پرداخت توسط کاربر لغو شد.',
            'purchase': purchase,
        })

    result = verify_payment(authority, purchase.amount)

    if result['ok']:
        purchase.status   = Purchase.Status.SUCCESS
        purchase.zp_ref_id= result['ref_id']
        purchase.authority= authority
        purchase.paid_at  = timezone.now()
        purchase.save(update_fields=['status', 'zp_ref_id', 'authority', 'paid_at'])

        obj = _get_content_object(purchase.content_type, purchase.object_id)
        return render(request, 'purchase/result.html', {
            'success':      True,
            'message':      'پرداخت موفق بود!',
            'purchase':     purchase,
            'content_url':  _content_redirect(purchase.content_type, obj),
            'ref_id':       result['ref_id'],
        })
    else:
        purchase.status = Purchase.Status.FAILED
        purchase.save(update_fields=['status'])
        return render(request, 'purchase/result.html', {
            'success': False,
            'message': f'تأیید پرداخت ناموفق: {result["error"]}',
            'purchase': purchase,
        })