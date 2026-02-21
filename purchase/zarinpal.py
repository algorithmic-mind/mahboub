"""
purchase/zarinpal.py
یکپارچه‌سازی با درگاه پرداخت زرین‌پال (REST v4)
"""
import requests
from django.conf import settings

SANDBOX = getattr(settings, 'ZARINPAL_SANDBOX', True)

if SANDBOX:
    REQUEST_URL  = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
    VERIFY_URL   = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
    GATEWAY_URL  = 'https://sandbox.zarinpal.com/pg/StartPay/{authority}'
else:
    REQUEST_URL  = 'https://api.zarinpal.com/pg/v4/payment/request.json'
    VERIFY_URL   = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
    GATEWAY_URL  = 'https://www.zarinpal.com/pg/StartPay/{authority}'

MERCHANT_ID  = getattr(settings, 'ZARINPAL_MERCHANT_ID', 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')


def request_payment(amount_toman: int, description: str, callback_url: str, mobile: str = '') -> dict:
    """
    درخواست پرداخت
    Returns: {'ok': True, 'authority': '...', 'gateway_url': '...'}
          or {'ok': False, 'error': '...'}
    """
    payload = {
        'merchant_id':   MERCHANT_ID,
        'amount':        amount_toman * 10,   # تبدیل به ریال
        'description':   description,
        'callback_url':  callback_url,
    }
    if mobile:
        payload['metadata'] = {'mobile': mobile}

    try:
        resp = requests.post(REQUEST_URL, json=payload, timeout=10)
        data = resp.json()
        if data.get('data', {}).get('code') == 100:
            authority = data['data']['authority']
            return {
                'ok': True,
                'authority': authority,
                'gateway_url': GATEWAY_URL.format(authority=authority)
            }
        return {'ok': False, 'error': data.get('errors', {}).get('message', 'خطای نامشخص')}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def verify_payment(authority: str, amount_toman: int) -> dict:
    """
    تأیید پرداخت
    Returns: {'ok': True, 'ref_id': '...'}
          or {'ok': False, 'error': '...'}
    """
    payload = {
        'merchant_id': MERCHANT_ID,
        'amount':      amount_toman * 10,
        'authority':   authority,
    }
    try:
        resp = requests.post(VERIFY_URL, json=payload, timeout=10)
        data = resp.json()
        code = data.get('data', {}).get('code')
        if code in (100, 101):      # 101 = قبلاً تأیید شده
            return {'ok': True, 'ref_id': str(data['data']['ref_id'])}
        return {'ok': False, 'error': data.get('errors', {}).get('message', 'پرداخت تأیید نشد')}
    except Exception as e:
        return {'ok': False, 'error': str(e)}