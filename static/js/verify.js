// verify.js - مدیریت صفحه تایید کد

class VerifyApp {
    constructor() {
        this.code = '';
        this.timeLeft = 120; // 2 minutes
        this.timerInterval = null;
        this.init();
    }

    init() {
        this.displayMobileNumber();
        this.initCodeInputs();
        this.initButtons();
        this.startTimer();
        this.initThemeAwareness();
    }

    initThemeAwareness() {
        // اطمینان از آپدیت استایل در تغییر تم
        document.addEventListener('themeChanged', () => {
            this.updateTimerDisplay();
        });
    }

    displayMobileNumber() {
        const mobile = localStorage.getItem('pendingMobile') || '۰۹۱۲۳۴۵۶۷۸۹';
        const displayMobile = document.getElementById('displayMobile');
        if (displayMobile) {
            displayMobile.textContent = this.formatMobileDisplay(mobile);
        }
    }

    formatMobileDisplay(mobile) {
        // Format: 0912 345 6789
        const persianMobile = this.toPersianNumber(mobile.replace(/\d/g, d => d));
        if (persianMobile.length === 11) {
            return persianMobile.slice(0, 4) + ' ' + persianMobile.slice(4, 7) + ' ' + persianMobile.slice(7);
        }
        return persianMobile;
    }

    initCodeInputs() {
        const inputs = document.querySelectorAll('.code-input');
        const verifyBtn = document.getElementById('verifyBtn');

        inputs.forEach((input, index) => {
            // ورودی فقط اعداد
            input.addEventListener('input', (e) => {
                e.target.value = e.target.value.replace(/[^0-9]/g, '');
                
                if (e.target.value.length === 1) {
                    e.target.classList.add('filled');
                    // رفتن به input بعدی
                    if (index < inputs.length - 1) {
                        inputs[index + 1].focus();
                    }
                } else {
                    e.target.classList.remove('filled');
                }

                // بررسی کامل بودن کد
                this.checkCodeComplete();
            });

            // پاک کردن و برگشت به عقب
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && !e.target.value && index > 0) {
                    inputs[index - 1].focus();
                    inputs[index - 1].value = '';
                    inputs[index - 1].classList.remove('filled');
                }

                // جابجایی با arrow keys (با در نظر گرفتن RTL)
                if (e.key === 'ArrowLeft' && index > 0) {
                    inputs[index - 1].focus();
                }
                if (e.key === 'ArrowRight' && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
            });

            // Paste handling
            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const pastedData = e.clipboardData.getData('text').replace(/[^0-9]/g, '');
                
                if (pastedData.length === 5) {
                    inputs.forEach((inp, idx) => {
                        inp.value = pastedData[idx] || '';
                        if (inp.value) inp.classList.add('filled');
                    });
                    inputs[4].focus();
                    this.checkCodeComplete();
                }
            });
        });

        // Focus اولین input
        setTimeout(() => inputs[0]?.focus(), 100);
    }

    checkCodeComplete() {
        const inputs = document.querySelectorAll('.code-input');
        const verifyBtn = document.getElementById('verifyBtn');
        
        this.code = Array.from(inputs).map(input => input.value).join('');
        
        verifyBtn.disabled = this.code.length !== 5;
    }

    initButtons() {
        const verifyBtn = document.getElementById('verifyBtn');
        const resendBtn = document.getElementById('resendBtn');
        const changeNumberBtn = document.getElementById('changeNumberBtn');

        verifyBtn?.addEventListener('click', () => this.verifyCode());
        resendBtn?.addEventListener('click', () => this.resendCode());
        changeNumberBtn?.addEventListener('click', () => this.changeNumber());
    }

    startTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        
        this.updateTimerDisplay();
        
        this.timerInterval = setInterval(() => {
            this.timeLeft--;
            this.updateTimerDisplay();

            if (this.timeLeft <= 0) {
                this.enableResend();
            }
        }, 1000);
    }

    updateTimerDisplay() {
        const timerEl = document.getElementById('timer');
        if (!timerEl) return;
        
        const minutes = Math.floor(Math.max(0, this.timeLeft) / 60);
        const seconds = Math.max(0, this.timeLeft) % 60;
        
        timerEl.textContent = `${this.toPersianNumber(minutes.toString().padStart(2, '0'))}:${this.toPersianNumber(seconds.toString().padStart(2, '0'))}`;
    }

    enableResend() {
        clearInterval(this.timerInterval);
        const resendBtn = document.getElementById('resendBtn');
        const resendText = document.getElementById('resendText');
        
        if (resendBtn) resendBtn.disabled = false;
        if (resendText) {
            resendText.innerHTML = '<span style="color: var(--danger);">زمان اعتبار کد به پایان رسید</span>';
        }
    }

    async verifyCode() {
        const verifyBtn = document.getElementById('verifyBtn');
        const originalText = verifyBtn.innerHTML;
        
        // نمایش لودینگ
        verifyBtn.disabled = true;
        verifyBtn.innerHTML = `
            <span>در حال تایید...</span>
            <i class="fas fa-spinner fa-spin"></i>
        `;

        // شبیه‌سازی تایید کد
        await new Promise(resolve => setTimeout(resolve, 1500));

        // بررسی کد (در حالت واقعی باید با سرور چک شود)
        if (this.code === '12345') {
            // کد صحیح
            this.showNotification('✓ ورود موفقیت‌آمیز بود', 'success');
            localStorage.removeItem('pendingMobile');
            localStorage.setItem('isLoggedIn', 'true');
            
            setTimeout(() => {
                window.location.href = 'profile.html';
            }, 1000);
        } else {
            // کد نادرست
            this.showNotification('کد وارد شده صحیح نیست', 'error');
            this.shakeInputs();
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = originalText;
            this.clearInputs();
        }
    }

    async resendCode() {
        const resendBtn = document.getElementById('resendBtn');
        const originalText = resendBtn.innerHTML;
        
        resendBtn.disabled = true;
        resendBtn.innerHTML = `
            <i class="fas fa-spinner fa-spin"></i>
            در حال ارسال...
        `;

        // شبیه‌سازی ارسال مجدد
        await new Promise(resolve => setTimeout(resolve, 1500));

        this.showNotification('کد تایید مجدداً ارسال شد');
        
        // Reset timer
        this.timeLeft = 120;
        this.startTimer();
        
        resendBtn.innerHTML = originalText;
        
        const resendText = document.getElementById('resendText');
        if (resendText) {
            resendText.innerHTML = '<span class="timer" id="timer"></span>';
            this.updateTimerDisplay();
        }
    }

    changeNumber() {
        window.location.href = 'login.html';
    }

    shakeInputs() {
        const inputs = document.querySelectorAll('.code-input');
        inputs.forEach(input => {
            input.classList.add('error');
            setTimeout(() => input.classList.remove('error'), 300);
        });
    }

    clearInputs() {
        const inputs = document.querySelectorAll('.code-input');
        inputs.forEach(input => {
            input.value = '';
            input.classList.remove('filled');
        });
        inputs[0]?.focus();
    }

    toPersianNumber(num) {
        const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
        return num.toString().replace(/\d/g, digit => persianDigits[parseInt(digit)]);
    }

    showNotification(message, type = 'info') {
        // حذف نوتیفیکیشن‌های قبلی
        const oldNotifications = document.querySelectorAll('.notification');
        oldNotifications.forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        
        let bgColor = 'var(--card-bg)';
        let textColor = 'var(--text-primary)';
        
        if (type === 'success') {
            bgColor = 'var(--success)';
            textColor = 'white';
        }
        if (type === 'error') {
            bgColor = 'var(--danger)';
            textColor = 'white';
        }
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${bgColor};
            color: ${textColor};
            padding: 14px 24px;
            border-radius: 8px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            font-size: 14px;
            font-weight: 500;
            animation: slideDown 0.3s ease;
            max-width: 90%;
            text-align: center;
            border: 1px solid var(--gray-200);
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2500);
    }
}

// شروع اپلیکیشن بعد از لود کامل DOM
document.addEventListener('DOMContentLoaded', () => {
    window.verifyApp = new VerifyApp();
});