// books.js - مدیریت صفحه کتاب‌ها

class BooksApp {
    constructor() {
        this.init();
    }

    init() {
        this.initDrawer();
        this.initSearchModal();
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.booksApp = new BooksApp();
});