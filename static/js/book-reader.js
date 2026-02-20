// book-reader.js - مدیریت صفحه خواندن کتاب

class BookReader {
    constructor() {
        this.currentPage = 1;
        this.totalPages = 2500;
        this.fontSize = 16;
        this.lineHeight = 1.8;
        this.selectedText = '';
        this.init();
    }

    init() {
        this.initContextMenu();
        this.initSettings();
        this.initNavigation();
        this.preventDefaultContextMenu();
    }

    // غیرفعال کردن منوی راست کلیک پیش‌فرض
    preventDefaultContextMenu() {
        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            return false;
        });

        // غیرفعال کردن کپی از طریق کیبورد
        document.addEventListener('keydown', (e) => {
            // جلوگیری از Ctrl+C, Ctrl+A, Ctrl+X, Ctrl+V
            if ((e.ctrlKey || e.metaKey) && ['c', 'a', 'x', 'v'].includes(e.key)) {
                e.preventDefault();
                return false;
            }
        });

        // غیرفعال کردن drag and drop
        document.addEventListener('dragstart', (e) => {
            e.preventDefault();
            return false;
        });

        // غیرفعال کردن copy event
        document.addEventListener('copy', (e) => {
            e.preventDefault();
            return false;
        });
    }

    // منوی راست کلیک اختصاصی
    initContextMenu() {
        const readerContent = document.getElementById('readerContent');
        const contextMenu = document.getElementById('contextMenu');

        // نمایش منوی اختصاصی
        readerContent.addEventListener('mouseup', (e) => {
            const selectedText = window.getSelection().toString().trim();
            
            if (selectedText.length > 0) {
                this.selectedText = selectedText;
                this.showContextMenu(e.pageX, e.pageY);
            } else {
                this.hideContextMenu();
            }
        });

        // بستن منو با کلیک در جای دیگر
        document.addEventListener('click', (e) => {
            if (!contextMenu.contains(e.target)) {
                this.hideContextMenu();
            }
        });

        // رویدادهای آیتم‌های منو
        document.getElementById('searchDictionary')?.addEventListener('click', () => {
            this.searchInDictionary();
        });

        document.getElementById('highlightText')?.addEventListener('click', () => {
            this.highlightSelectedText();
        });

        document.getElementById('addNote')?.addEventListener('click', () => {
            this.addNoteToText();
        });
    }

    showContextMenu(x, y) {
        const contextMenu = document.getElementById('contextMenu');
        contextMenu.classList.add('active');
        
        // تنظیم موقعیت منو
        const menuWidth = 220;
        const menuHeight = 200;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        let left = x;
        let top = y;

        // اطمینان از اینکه منو از صفحه خارج نشود
        if (x + menuWidth > windowWidth) {
            left = windowWidth - menuWidth - 10;
        }

        if (y + menuHeight > windowHeight) {
            top = windowHeight - menuHeight - 10;
        }

        contextMenu.style.left = left + 'px';
        contextMenu.style.top = top + 'px';
    }

    hideContextMenu() {
        const contextMenu = document.getElementById('contextMenu');
        contextMenu.classList.remove('active');
    }

    searchInDictionary() {
        if (this.selectedText) {
            this.showNotification(`جستجوی "${this.selectedText}" در دیکشنری محبوب...`);
            // شبیه‌سازی جستجو در دیکشنری
            setTimeout(() => {
                this.showDictionaryResult(this.selectedText);
            }, 800);
        }
        this.hideContextMenu();
    }

    showDictionaryResult(word) {
        // نمایش نتیجه جستجو در دیکشنری (شبیه‌سازی)
        const definitions = {
            'تدبر': 'تفکر عمیق و دقیق در معانی و مفاهیم',
            'هدایت': 'راهنمایی به سوی راه حق و کمال',
            'برهان': 'دلیل و استدلال عقلی',
            'default': 'در حال جستجوی تعریف دقیق...'
        };

        const definition = definitions[word] || definitions['default'];
        this.showNotification(`📖 ${word}: ${definition}`, 4000);
    }

    highlightSelectedText() {
        if (this.selectedText) {
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                const span = document.createElement('span');
                span.className = 'highlighted';
                range.surroundContents(span);
                this.showNotification('متن هایلایت شد');
            }
        }
        this.hideContextMenu();
        window.getSelection().removeAllRanges();
    }

    addNoteToText() {
        if (this.selectedText) {
            const note = prompt('یادداشت خود را وارد کنید:');
            if (note) {
                this.showNotification('یادداشت ذخیره شد');
                // ذخیره یادداشت (در localStorage یا سرور)
                console.log('Note added:', { text: this.selectedText, note: note });
            }
        }
        this.hideContextMenu();
    }

    // تنظیمات خواندن
    initSettings() {
        const settingsBtn = document.getElementById('settingsBtn');
        const settingsPanel = document.getElementById('settingsPanel');
        const settingsClose = document.getElementById('settingsClose');
        const readerContent = document.querySelector('.reader-page');
        const themeSwitch = document.getElementById('themeSwitch');

        settingsBtn?.addEventListener('click', () => {
            settingsPanel.classList.add('active');
        });

        settingsClose?.addEventListener('click', () => {
            settingsPanel.classList.remove('active');
        });

        // تغییر تم
        themeSwitch?.addEventListener('click', () => {
            if (window.themeManager) {
                window.themeManager.toggleTheme();
            }
        });

        // تنظیم اندازه فونت
        document.getElementById('increaseFont')?.addEventListener('click', () => {
            if (this.fontSize < 24) {
                this.fontSize += 2;
                this.applyFontSize();
            }
        });

        document.getElementById('decreaseFont')?.addEventListener('click', () => {
            if (this.fontSize > 12) {
                this.fontSize -= 2;
                this.applyFontSize();
            }
        });

        // تنظیم فاصله خطوط
        document.querySelectorAll('.line-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.line-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.lineHeight = parseFloat(e.target.dataset.height);
                this.applyLineHeight();
            });
        });

        // نشان کردن کتاب
        document.getElementById('bookmarkReaderBtn')?.addEventListener('click', (e) => {
            const icon = e.currentTarget.querySelector('i');
            if (icon.classList.contains('far')) {
                icon.className = 'fas fa-bookmark';
                this.showNotification('صفحه نشان شد');
            } else {
                icon.className = 'far fa-bookmark';
                this.showNotification('نشان حذف شد');
            }
        });
    }

    applyFontSize() {
        const readerTexts = document.querySelectorAll('.reader-text');
        readerTexts.forEach(text => {
            text.style.fontSize = this.fontSize + 'px';
        });
        document.getElementById('fontSizeDisplay').textContent = this.fontSize;
    }

    applyLineHeight() {
        const readerPage = document.querySelector('.reader-page');
        readerPage.style.lineHeight = this.lineHeight;
    }

    // ناوبری صفحات
    initNavigation() {
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        const progressSlider = document.getElementById('progressSlider');

        prevBtn?.addEventListener('click', () => this.previousPage());
        nextBtn?.addEventListener('click', () => this.nextPage());

        progressSlider?.addEventListener('input', (e) => {
            this.goToPage(parseInt(e.target.value));
        });

        // کیبورد شورتکات
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') this.previousPage();
            else if (e.key === 'ArrowLeft') this.nextPage();
        });

        this.updatePageDisplay();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.updatePageDisplay();
            this.scrollToTop();
        }
    }

    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage++;
            this.updatePageDisplay();
            this.scrollToTop();
        }
    }

    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.currentPage = page;
            this.updatePageDisplay();
            this.scrollToTop();
        }
    }

    updatePageDisplay() {
        const currentPageEl = document.getElementById('currentPage');
        const progressSlider = document.getElementById('progressSlider');
        const pageIndicator = document.querySelector('.reader-title p');

        if (currentPageEl) currentPageEl.textContent = this.currentPage;
        if (progressSlider) progressSlider.value = this.currentPage;
        if (pageIndicator) pageIndicator.textContent = `صفحه ${this.currentPage} از ${this.totalPages}`;

        // غیرفعال کردن دکمه‌ها در صورت نیاز
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');

        if (prevBtn) prevBtn.disabled = this.currentPage === 1;
        if (nextBtn) nextBtn.disabled = this.currentPage === this.totalPages;
    }

    scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showNotification(message, duration = 2500) {
        const notification = document.createElement('div');
        notification.className = 'reader-notification';
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
            z-index: 10000;
            font-size: 14px;
            font-weight: 500;
            border: 1px solid var(--gray-200);
            animation: slideDown 0.3s ease;
            max-width: 90%;
            text-align: center;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
}

// انیمیشن‌های CSS
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
    window.bookReader = new BookReader();
});
