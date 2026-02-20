// book-detail.js - مدیریت صفحه جزئیات کتاب

class BookDetailApp {
    constructor() {
        this.isBookmarked = false;
        this.init();
    }

    init() {
        this.initButtons();
    }

    initButtons() {
        const bookmarkBtn = document.getElementById('bookmarkBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const shareBtn = document.getElementById('shareBtn');
        const shareToggle = document.getElementById('shareToggle');
        const purchaseBtn = document.getElementById('purchaseBtn');
        const previewBtn = document.getElementById('previewBtn');

        bookmarkBtn?.addEventListener('click', () => this.toggleBookmark());
        downloadBtn?.addEventListener('click', () => this.downloadSample());
        shareBtn?.addEventListener('click', () => this.shareBook());
        shareToggle?.addEventListener('click', () => this.shareBook());
        purchaseBtn?.addEventListener('click', () => this.purchaseBook());
        previewBtn?.addEventListener('click', () => this.previewBook());
    }

    toggleBookmark() {
        const bookmarkBtn = document.getElementById('bookmarkBtn');
        const icon = bookmarkBtn?.querySelector('i');
        
        this.isBookmarked = !this.isBookmarked;
        
        if (icon) {
            if (this.isBookmarked) {
                icon.className = 'fas fa-bookmark';
                this.showNotification('کتاب نشان شد');
            } else {
                icon.className = 'far fa-bookmark';
                this.showNotification('نشان حذف شد');
            }
        }
    }

    downloadSample() {
        this.showNotification('در حال دانلود   ...');
        // Simulate download
        setTimeout(() => {
            this.showNotification('   کتاب دانلود شد');
        }, 1500);
    }

    shareBook() {
        if (navigator.share) {
            navigator.share({
                title: 'تفسیر المیزان',
                text: 'این کتاب را در محبوب ببینید',
                url: window.location.href
            }).catch(err => console.log('خطا در اشتراک‌گذاری:', err));
        } else {
            // Fallback: کپی لینک
            navigator.clipboard.writeText(window.location.href);
            this.showNotification('لینک کپی شد');
        }
    }

    purchaseBook() {
        this.showNotification('در حال انتقال به صفحه پرداخت...');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1000);
    }

    previewBook() {
        this.showNotification('در حال بارگذاری   ...');
        setTimeout(() => {
            window.location.href = 'book-reader.html';
        }, 1000);
    }

    showNotification(message) {
        // ساخت المنت نوتیفیکیشن
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

document.addEventListener('DOMContentLoaded', () => {
    window.bookDetailApp = new BookDetailApp();
});