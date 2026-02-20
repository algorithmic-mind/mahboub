// podcasts.js - مدیریت صفحه پادکست‌ها

class PodcastsApp {
    constructor() {
        this.init();
    }

    init() {
        this.initDrawer();
        this.initSearchModal();
        this.initPlayButtons();
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

    initSearchModal() {
        const searchToggle = document.getElementById('searchToggle');
        const searchModal = document.getElementById('searchModal');
        const searchBackdrop = document.getElementById('searchBackdrop');
        const searchClose = document.getElementById('searchClose');
        const searchInput = document.getElementById('searchInput');

        const openSearch = () => {
            searchModal?.classList.add('active');
            document.body.style.overflow = 'hidden';
            setTimeout(() => searchInput?.focus(), 300);
        };

        const closeSearch = () => {
            searchModal?.classList.remove('active');
            document.body.style.overflow = '';
            if (searchInput) searchInput.value = '';
        };

        searchToggle?.addEventListener('click', openSearch);
        searchBackdrop?.addEventListener('click', closeSearch);
        searchClose?.addEventListener('click', closeSearch);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchModal?.classList.contains('active')) {
                closeSearch();
            }
        });
    }

    initPlayButtons() {
        const playButtons = document.querySelectorAll('.podcast-play-btn, .featured-play-btn');
        
        playButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.playPodcast(e.currentTarget);
            });
        });
    }

    playPodcast(button) {
        const icon = button.querySelector('i');
        
        // Toggle play/pause
        if (icon.classList.contains('fa-play')) {
            icon.classList.remove('fa-play');
            icon.classList.add('fa-pause');
            this.showNotification('پخش پادکست...');
        } else {
            icon.classList.remove('fa-pause');
            icon.classList.add('fa-play');
            this.showNotification('پخش متوقف شد');
        }
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 90px;
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
            animation: slideUp 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.podcastsApp = new PodcastsApp();
});