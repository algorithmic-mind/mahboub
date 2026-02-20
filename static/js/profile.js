// profile.js - مدیریت صفحه پروفایل

class ProfileApp {
    constructor() {
        this.init();
    }

    init() {
        this.initDrawer();
        this.initDarkMode();
        this.initLogout();
    }

    initDrawer() {
        const menuToggle = document.getElementById('menuToggle');
        const drawerMenu = document.getElementById('drawerMenu');
        const drawerBackdrop = document.getElementById('drawerBackdrop');
        const drawerClose = document.getElementById('drawerClose');

        const openDrawer = () => {
            drawerMenu?.classList.add('active');
            drawerBackdrop?.classList.add('active');
            document.body.style.overflow = 'hidden';
        };

        const closeDrawer = () => {
            drawerMenu?.classList.remove('active');
            drawerBackdrop?.classList.remove('active');
            document.body.style.overflow = '';
        };

        menuToggle?.addEventListener('click', openDrawer);
        drawerBackdrop?.addEventListener('click', closeDrawer);
        drawerClose?.addEventListener('click', closeDrawer);
    }

    initDarkMode() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        
        if (darkModeToggle) {
            // Set initial state
            const isDark = document.documentElement.hasAttribute('data-theme');
            darkModeToggle.checked = isDark;

            // Toggle handler
            darkModeToggle.addEventListener('change', (e) => {
                if (window.themeManager) {
                    window.themeManager.toggleTheme();
                }
            });

            // Listen to theme changes
            window.addEventListener('theme-changed', (e) => {
                darkModeToggle.checked = e.detail.isDark;
            });
        }
    }

    initLogout() {
        const logoutBtn = document.getElementById('logoutBtn');

        logoutBtn?.addEventListener('click', () => {
            if (confirm('آیا مطمئن هستید که می‌خواهید از حساب کاربری خود خارج شوید؟')) {
                this.logout();
            }
        });
    }

    logout() {
        // پاک کردن اطلاعات ورود
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('pendingMobile');

        this.showNotification('خروج موفقیت‌آمیز بود');

        // انتقال به صفحه ورود
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1000);
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--card-bg);
            color: var(--text-primary);
            padding: 12px 24px;
            border-radius: 8px;
            box-shadow: var(--shadow-xl);
            z-index: 1000;
            font-size: 14px;
            font-weight: 500;
            border: 1px solid var(--gray-200);
            animation: slideDown 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
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
    window.profileApp = new ProfileApp();
});