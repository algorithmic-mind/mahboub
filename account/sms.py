import random
import logging
from django.conf import settings
from sms_ir import SmsIr
import requests
logger = logging.getLogger(__name__)


def generate_otp(length=None):
    """تولید کد OTP تصادفی"""
    length = length or getattr(settings, 'OTP_LENGTH', 5)
    return str(random.randint(10 ** (length - 1), 10**length - 1))


def send_otp_sms(phone_number, otp_code) -> bool:
    """
    ارسال کد OTP از طریق sms.ir
    
    phone_number: شماره با فرمت 09xxxxxxxxx
    otp_code: کد عددی
    returns: True در صورت موفقیت
    """
    phone_number = phone_number
    try:
        from sms_ir import SmsIr  # pip install smsir-python
        
        api_key = settings.SMSIR_API_KEY
        template_id = settings.SMSIR_TEMPLATE_ID

       

        sms_ir = SmsIr(api_key)
        sms_ir.send_verify_code(
            number=phone_number,
            template_id=template_id,
            parameters=[
                {
                    "name": "CODE",
                    "value": str(otp_code),
                },
            ],
        )
        logger.info(f"OTP sent to {phone_number}")
        return True

    except ImportError:
        # حالت توسعه: فقط لاگ کن
        logger.warning(f"[DEV MODE] OTP for {phone_number}: {otp_code}")
        print(f"\n{'='*40}")
        print(f"[DEV] OTP Code for {phone_number}: {otp_code}")
        print(f"{'='*40}\n")
        return True

    except Exception as e:
        logger.error(f"SMS sending failed for {phone_number}: {e}")
        return False