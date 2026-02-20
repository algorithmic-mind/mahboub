// js/main.js - نسخه بهینه شده

class LibraryApp {
    constructor() {
        this.currentSlide = 0;
        this.slides = [];
        this.sliderInterval = null;
        this.slideDuration = 5000;
        this.isSearchModalOpen = false;
        this.init();
    }

    init() {
        this.initDrawer();
        this.initSlider();
        this.initSearchModal();
        this.initEventListeners();
        this.initCategoryTabs();
        this.startAutoSlide();
        this.initAIWelcomeModal();
    }

    initAIWelcomeModal() {
        this.aiWelcomeModal = document.getElementById('aiWelcomeModal');
        this.aiWelcomeBackdrop = document.getElementById('aiWelcomeBackdrop');
        this.aiWelcomeClose = document.getElementById('aiWelcomeClose');
        this.aiWelcomeLater = document.getElementById('aiWelcomeLater');
        this.aiWelcomeDontShow = document.getElementById('aiWelcomeDontShow');

        // بررسی اینکه آیا قبلاً کاربر گفته "دیگر نشان نده"
        const dontShowAgain = localStorage.getItem('aiWelcomeDontShow');
        
        if (!dontShowAgain) {
            // نمایش پاپ آپ با تاخیر 1 ثانیه
            setTimeout(() => {
                this.showAIWelcomeModal();
            }, 1000);
        }

        // رویداد بستن
        this.aiWelcomeClose?.addEventListener('click', () => this.closeAIWelcomeModal());
        this.aiWelcomeBackdrop?.addEventListener('click', () => this.closeAIWelcomeModal());
        this.aiWelcomeLater?.addEventListener('click', () => this.closeAIWelcomeModal());
    }

    showAIWelcomeModal() {
        if (!this.aiWelcomeModal) return;
        this.aiWelcomeModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeAIWelcomeModal() {
        if (!this.aiWelcomeModal) return;
        
        // بررسی چک باکس "دیگر نشان نده"
        if (this.aiWelcomeDontShow?.checked) {
            localStorage.setItem('aiWelcomeDontShow', 'true');
        }
        
        this.aiWelcomeModal.classList.remove('active');
        document.body.style.overflow = '';
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

    initSlider() {
        const slider = document.getElementById('imageSlider');
        if (!slider) return;

        this.slides = Array.from(slider.querySelectorAll('.slider-slide'));
        this.dots = Array.from(slider.querySelectorAll('.slider-dot'));
        this.prevBtn = slider.querySelector('.slider-prev');
        this.nextBtn = slider.querySelector('.slider-next');

        if (this.slides.length > 0) {
            this.showSlide(0);
        }
    }

    initSearchModal() {
        this.searchModal = document.getElementById('searchModal');
        this.searchToggle = document.getElementById('searchToggle');
        this.searchBackdrop = document.getElementById('searchBackdrop');
        this.searchClose = document.getElementById('searchClose');
        this.searchInput = document.getElementById('searchInput');
    }

    showSlide(index) {
        if (this.slides.length === 0) return;

        if (index < 0) index = this.slides.length - 1;
        else if (index >= this.slides.length) index = 0;

        this.slides.forEach(slide => slide.classList.remove('active'));
        this.dots.forEach(dot => dot.classList.remove('active'));

        this.slides[index].classList.add('active');
        if (this.dots[index]) this.dots[index].classList.add('active');
        this.currentSlide = index;
    }

    nextSlide() {
        this.showSlide(this.currentSlide + 1);
        this.resetAutoSlide();
    }

    prevSlide() {
        this.showSlide(this.currentSlide - 1);
        this.resetAutoSlide();
    }

    goToSlide(index) {
        this.showSlide(index);
        this.resetAutoSlide();
    }

    startAutoSlide() {
        if (this.slides.length <= 1) return;
        this.sliderInterval = setInterval(() => this.nextSlide(), this.slideDuration);
    }

    resetAutoSlide() {
        if (this.sliderInterval) {
            clearInterval(this.sliderInterval);
            this.startAutoSlide();
        }
    }

    stopAutoSlide() {
        if (this.sliderInterval) {
            clearInterval(this.sliderInterval);
            this.sliderInterval = null;
        }
    }

    openSearchModal() {
        if (!this.searchModal) return;
        this.searchModal.classList.add('active');
        this.isSearchModalOpen = true;
        document.body.style.overflow = 'hidden';
        setTimeout(() => this.searchInput?.focus(), 300);
    }

    closeSearchModal() {
        if (!this.searchModal) return;
        this.searchModal.classList.remove('active');
        this.isSearchModalOpen = false;
        document.body.style.overflow = '';
        if (this.searchInput) this.searchInput.value = '';
    }

    performSearch(query) {
        if (!query.trim()) return;
        console.log('جستجو برای:', query);
        this.closeSearchModal();
    }

    initCategoryTabs() {
        const categoryTabs = document.querySelectorAll('#categoryTabsIndex .category-tab');
        if (categoryTabs.length === 0) return;

        categoryTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const activeTab = e.currentTarget;
                const category = activeTab.dataset.category;
                
                categoryTabs.forEach(t => t.classList.remove('active'));
                activeTab.classList.add('active');
                this.filterCategoryBooks(category);
            });
        });

        // Podcasts category tabs
        const podcastTabs = document.querySelectorAll('#categoryTabsPodcasts .category-tab');
        podcastTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const activeTab = e.currentTarget;
                const category = activeTab.dataset.category;
                
                podcastTabs.forEach(t => t.classList.remove('active'));
                activeTab.classList.add('active');
                this.filterPodcasts(category);
            });
        });

        // Videos category tabs
        const videoTabs = document.querySelectorAll('#categoryTabsVideos .category-tab');
        videoTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const activeTab = e.currentTarget;
                const category = activeTab.dataset.category;
                
                videoTabs.forEach(t => t.classList.remove('active'));
                activeTab.classList.add('active');
                this.filterVideos(category);
            });
        });
    }

    filterCategoryBooks(category) {
        const booksContainer = document.querySelector('.books-categories-container');
        if (!booksContainer) return;

        const categoryRows = booksContainer.querySelectorAll('.category-books-row');
        
        categoryRows.forEach(row => {
            const rowCategory = row.dataset.category;
            
            if (category === 'all' || rowCategory === category) {
                row.style.display = 'block';
                row.style.animation = 'fadeIn 0.3s ease';
            } else {
                row.style.display = 'none';
            }
        });
    }

    filterPodcasts(category) {
        const podcastsContainer = document.querySelector('.podcasts-categories-container');
        if (!podcastsContainer) return;

        const categoryRows = podcastsContainer.querySelectorAll('.category-podcasts-row');
        
        categoryRows.forEach(row => {
            const rowCategory = row.dataset.category;
            
            if (category === 'all' || rowCategory === category) {
                row.style.display = 'block';
                row.style.animation = 'fadeIn 0.3s ease';
            } else {
                row.style.display = 'none';
            }
        });
    }

    filterVideos(category) {
        const videosContainer = document.querySelector('.videos-categories-container');
        if (!videosContainer) return;

        const categoryRows = videosContainer.querySelectorAll('.category-videos-row');
        
        categoryRows.forEach(row => {
            const rowCategory = row.dataset.category;
            
            if (category === 'all' || rowCategory === category) {
                row.style.display = 'block';
                row.style.animation = 'fadeIn 0.3s ease';
            } else {
                row.style.display = 'none';
            }
        });
    }

    initEventListeners() {
        this.searchToggle?.addEventListener('click', () => this.openSearchModal());
        this.searchBackdrop?.addEventListener('click', () => this.closeSearchModal());
        this.searchClose?.addEventListener('click', () => this.closeSearchModal());

        if (this.searchInput) {
            this.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.performSearch(this.searchInput.value);
            });
        }

        const searchBtn = document.querySelector('.search-input-btn');
        searchBtn?.addEventListener('click', () => {
            if (this.searchInput) this.performSearch(this.searchInput.value);
        });

        document.querySelectorAll('.search-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                e.preventDefault();
                this.performSearch(tag.textContent);
            });
        });

        this.prevBtn?.addEventListener('click', () => this.prevSlide());
        this.nextBtn?.addEventListener('click', () => this.nextSlide());

        this.dots?.forEach((dot, index) => {
            dot.addEventListener('click', () => this.goToSlide(index));
        });

        this.initTouchEvents();

        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isSearchModalOpen) this.closeSearchModal();
        });
    }

    initTouchEvents() {
        const slider = document.getElementById('imageSlider');
        if (!slider) return;

        let touchStartX = 0;
        slider.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
            this.stopAutoSlide();
        }, { passive: true });

        slider.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe(touchStartX, touchEndX);
            this.startAutoSlide();
        }, { passive: true });
    }

    handleSwipe(startX, endX) {
        const swipeThreshold = 50;
        const diff = startX - endX;
        if (Math.abs(diff) > swipeThreshold) {
            diff > 0 ? this.nextSlide() : this.prevSlide();
        }
    }

    handleKeyDown(e) {
        if (this.isSearchModalOpen) return;
        if (e.key === 'ArrowRight') this.nextSlide();
        else if (e.key === 'ArrowLeft') this.prevSlide();
        else if (e.key === '/') {
            e.preventDefault();
            this.openSearchModal();
        }
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new LibraryApp();
});