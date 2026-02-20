// js/theme-manager.js - مدیریت متمرکز تم در کل برنامه

class ThemeManager {
    constructor() {
        this.currentTheme = this.getSavedTheme();
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.initEventListeners();
        this.observeThemeChanges();
    }

    getSavedTheme() {
        const savedTheme = localStorage.getItem('library-theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        return savedTheme || (prefersDark ? 'dark' : 'light');
    }

    applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        
        localStorage.setItem('library-theme', theme);
        this.currentTheme = theme;
        this.dispatchThemeChangeEvent();
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }

    initEventListeners() {
        document.addEventListener('click', (e) => {
            const themeToggle = e.target.closest('.theme-toggle, [id*="themeToggle"]');
            if (themeToggle) {
                this.toggleTheme();
                e.preventDefault();
            }
        });

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('library-theme')) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    observeThemeChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme') {
                    this.updateThemeIcons();
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    }

    updateThemeIcons() {
        const isDark = document.documentElement.hasAttribute('data-theme');
        const themeIcons = document.querySelectorAll('[id*="themeIcon"], [id*="themeToggle"] i');
        
        themeIcons.forEach(icon => {
            if (icon) {
                icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
            }
        });
    }

    dispatchThemeChangeEvent() {
        window.dispatchEvent(new CustomEvent('theme-changed', {
            detail: { 
                theme: this.currentTheme,
                isDark: this.currentTheme === 'dark'
            }
        }));
    }

    getCurrentTheme() {
        return this.currentTheme;
    }

    onThemeChange(callback) {
        window.addEventListener('theme-changed', (event) => {
            callback(event.detail);
        });
    }
}

window.themeManager = new ThemeManager();