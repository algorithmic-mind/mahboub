// login.js - مدیریت صفحه ورود

class LoginApp {
    constructor() {
        this.mobileNumber = '';
        this.init();
    }

    init() {
        this.initMobileInput();
        this.initButtons();
    }

    initMobileInput() {
        const mobileInput = document.getElementById('mobileInput');
        const sendCodeBtn = document.getElementById('sendCodeBtn');

        mobileInput?.addEventListener('input', (e) => {
            // فقط اجازه ورود اعداد
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
            
            this.mobileNumber = e.target.value;
            
            // فعال/غیرفعال کردن دکمه ارسال کد
            if (this.isValidMobile(this.mobileNumber)) {
                sendCodeBtn.disabled = false;
            } else {
                sendCodeBtn.disabled = true;
            }
        });

        // Auto-format mobile number
        
    }

    initButtons() {
        const sendCodeBtn = document.getElementById('sendCodeBtn');
        const termsLink = document.getElementById('termsLink');
        const termsModal = document.getElementById('termsModal');
        const termsModalClose = document.getElementById('termsModalClose');
        const termsAcceptBtn = document.getElementById('termsAcceptBtn');

        sendCodeBtn?.addEventListener('click', () => this.sendVerificationCode());
        
        // Terms modal handlers
        termsLink?.addEventListener('click', (e) => {
            e.preventDefault();
            this.openTermsModal();
        });
        
        termsModalClose?.addEventListener('click', () => this.closeTermsModal());
        termsAcceptBtn?.addEventListener('click', () => this.closeTermsModal());
        
        // Close on backdrop click
        termsModal?.addEventListener('click', (e) => {
            if (e.target === termsModal) {
                this.closeTermsModal();
            }
        });
    }

    isValidMobile(mobile) {
        // شماره موبایل باید 10 رقم باشد و با 9 شروع شود
        const cleaned = mobile.replace(/\s/g, '');
        return /^9[0-9]{9}$/.test(cleaned);
    }

    async sendVerificationCode() {
        const sendCodeBtn = document.getElementById('sendCodeBtn');
        const originalText = sendCodeBtn.innerHTML;
        
        // نمایش لودینگ
        sendCodeBtn.disabled = true;
        sendCodeBtn.innerHTML = `
            <span>در حال ارسال...</span>
            <i class="fas fa-spinner fa-spin"></i>
        `;

        // شبیه‌سازی ارسال کد
        await new Promise(resolve => setTimeout(resolve, 1500));

        // ذخیره شماره موبایل
        const cleanedMobile = this.mobileNumber.replace(/\s/g, '');
        localStorage.setItem('pendingMobile', '0' + cleanedMobile);

        // انتقال به صفحه تایید کد
        window.location.href = 'verify.html';
    }

    loginWithGoogle() {
        this.showNotification('قابلیت ورود با گوگل به زودی فعال می‌شود');
    }

    openTermsModal() {
        const termsModal = document.getElementById('termsModal');
        termsModal?.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeTermsModal() {
        const termsModal = document.getElementById('termsModal');
        termsModal?.classList.remove('active');
        document.body.style.overflow = '';
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            color: var(--text-primary);
            padding: 14px 24px;
            border-radius: 8px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            font-size: 14px;
            font-weight: 500;
            animation: slideDown 0.3s ease;
            max-width: 90%;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2500);
    }
}

// انیمیشن‌ها
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translate(-50%, -20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }

    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translate(-50%, 0);
        }
        to {
            opacity: 0;
            transform: translate(-50%, -20px);
        }
    }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
    window.loginApp = new LoginApp();
});