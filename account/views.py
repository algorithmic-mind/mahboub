import re
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator

from .models import User
from .sms import generate_otp, send_otp_sms


def is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


def validate_phone(phone: str) -> bool:
    """شماره 10 رقمی شروع با 9 (بدون صفر)"""
    return bool(re.match(r'^9[0-9]{9}$', phone))


# ─────────────────────────────────────────
# Login View
# ─────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('account:profile')
    return render(request, 'account/login.html')


@require_http_methods(["POST"])
def send_code(request):
    """HTMX endpoint: دریافت شماره → ارسال OTP"""
    phone_raw = request.POST.get('phone', '').strip()

    if not validate_phone(phone_raw):
        if is_htmx(request):
            return HttpResponse(
                '<div class="input-error">شماره موبایل معتبر نیست</div>',
                status=422
            )
        return redirect('account:login')

    phone = '0' + phone_raw  # ذخیره با صفر پیشرو

    # گرفتن یا ساخت کاربر
    user, created = User.objects.get_or_create(phone_number=phone)

    # تولید و ذخیره OTP
    otp = generate_otp()
    user.set_otp(otp)

    # ارسال SMS
    sms_sent = send_otp_sms(phone, otp)

    # ذخیره شماره در session برای مرحله verify
    request.session['pending_phone'] = phone
    request.session.modified = True

    if is_htmx(request):
        # جایگزین کردن محتوای فرم با فرم verify
        response = render(request, 'account/partials/verify_form.html', {
            'phone': phone,
            'phone_display': _format_phone(phone),
            'sms_sent': sms_sent,
        })
        response['HX-Push-Url'] = '/account/verify/'
        return response

    return redirect('account:verify')


# ─────────────────────────────────────────
# Verify View
# ─────────────────────────────────────────

def verify_view(request):
    phone = request.session.get('pending_phone')
    if not phone:
        return redirect('login')
    return render(request, 'account/verify.html', {
        'phone': phone,
        'phone_display': _format_phone(phone),
    })


@require_http_methods(["POST"])
def verify_code(request):
    """HTMX endpoint: تایید کد OTP"""
    phone = request.session.get('pending_phone')
    code = request.POST.get('code', '').strip()

    if not phone:
        if is_htmx(request):
            return HttpResponse(
                '<div class="input-error">جلسه منقضی شده. دوباره وارد شوید</div>',
                status=422
            )
        return redirect('account:login')

    try:
        user = User.objects.get(phone_number=phone)
    except User.DoesNotExist:
        if is_htmx(request):
            return HttpResponse(
                '<div class="input-error">کاربر یافت نشد</div>',
                status=422
            )
        return redirect('account:login')

    if not user.is_otp_valid(code):
        if is_htmx(request):
            return HttpResponse(
                '<div class="otp-error" id="otp-error">کد وارد شده صحیح یا منقضی شده است</div>',
                status=422,
                headers={'HX-Retarget': '#otp-error-container', 'HX-Reswap': 'innerHTML'}
            )
        return render(request, 'account/verify.html', {
            'phone': phone,
            'phone_display': _format_phone(phone),
            'error': 'کد وارد شده صحیح یا منقضی شده است',
        })

    # کد صحیح: ورود
    user.clear_otp()
    del request.session['pending_phone']
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    if is_htmx(request):
        response = HttpResponse(status=204)
        response['HX-Redirect'] = '/account/profile/'
        return response

    return redirect('account:profile')


@require_http_methods(["POST"])
def resend_code(request):
    """HTMX endpoint: ارسال مجدد کد"""
    phone = request.session.get('pending_phone')
    if not phone:
        return HttpResponse('<span class="resend-error">جلسه منقضی شده</span>', status=422)

    try:
        user = User.objects.get(phone_number=phone)
    except User.DoesNotExist:
        return HttpResponse('<span class="resend-error">کاربر یافت نشد</span>', status=422)

    otp = generate_otp()
    user.set_otp(otp)
    send_otp_sms(phone, otp)

    return HttpResponse(
        '<span class="resend-success">کد جدید ارسال شد ✓</span>',
    )


# ─────────────────────────────────────────
# Profile View
# ─────────────────────────────────────────

@login_required
def profile_view(request):
    return render(request, 'account/profile.html', {'user': request.user})


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    if is_htmx(request):
        response = HttpResponse(status=204)
        response['HX-Redirect'] = '/account/login/'
        return response
    return redirect('account:login')


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def _format_phone(phone: str) -> str:
    """09123456789 → 0912 345 6789"""
    if len(phone) == 11:
        return f"{phone[:4]} {phone[4:7]} {phone[7:]}"
    return phone