// estekhara.js - استخاره آنلاین

class Estekhara {
    constructor() {
        this.currentStep = 1;
        this.userQuestion = '';
        this.selectedAyah = null;
        this.init();
    }

    init() {
        this.initButtons();
    }

    initButtons() {
        document.getElementById('startBtn')?.addEventListener('click', () => this.goToStep(2));
        document.getElementById('openQuranBtn')?.addEventListener('click', () => this.openQuran());
        document.getElementById('shareBtn')?.addEventListener('click', () => this.shareResult());
        document.getElementById('newEstekharaBtn')?.addEventListener('click', () => this.resetEstekhara());
    }

    goToStep(step) {
        // Hide all steps
        document.querySelectorAll('.estekhara-step').forEach(s => s.classList.remove('active'));
        
        // Show target step
        document.getElementById(`step${step}`)?.classList.add('active');
        this.currentStep = step;

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    openQuran() {
        const question = document.getElementById('questionInput')?.value.trim();
        
        if (!question) {
            this.showNotification('لطفاً موضوع استخاره را وارد کنید');
            return;
        }

        this.userQuestion = question;
        this.goToStep(3);

        // Simulate opening Quran
        setTimeout(() => {
            this.performEstekhara();
        }, 3000);
    }

    performEstekhara() {
        // نمونه آیات قرآن برای استخاره
        const ayahs = [
            {
                surah: 'البقره',
                ayahNumber: '۲۸۶',
                text: 'لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا',
                translation: 'خداوند هیچ کس را جز به اندازه توانایی‌اش تکلیف نمی‌کند',
                interpretation: 'این آیه نشان می‌دهد که خداوند برای شما آسانی قرار داده است. در این کار با توکل به خدا پیش بروید و از توان خود استفاده کنید.',
                isPositive: true
            },
            {
                surah: 'یوسف',
                ayahNumber: '۸۷',
                text: 'وَلَا تَيْأَسُوا مِن رَّوْحِ اللَّهِ',
                translation: 'از رحمت خدا نومید نشوید',
                interpretation: 'این آیه به شما امید می‌دهد. هر چند ممکن است موانعی وجود داشته باشد، اما با امید به خدا و تلاش مستمر، به نتیجه خواهید رسید.',
                isPositive: true
            },
            {
                surah: 'الشرح',
                ayahNumber: '۶',
                text: 'إِنَّ مَعَ الْعُسْرِ يُسْرًا',
                translation: 'همانا با هر سختی آسانی است',
                interpretation: 'این آیه نوید آسانی را می‌دهد. اگر در ابتدا سختی احساس کردید، بدانید که پس از آن آسانی خواهد آمد. با صبر و استقامت ادامه دهید.',
                isPositive: true
            },
            {
                surah: 'الرحمن',
                ayahNumber: '۱۳',
                text: 'فَبِأَيِّ آلَاءِ رَبِّكُمَا تُكَذِّبَانِ',
                translation: 'پس کدام یک از نعمت‌های پروردگارتان را انکار می‌کنید',
                interpretation: 'خداوند نعمت‌های بسیاری به شما داده است. در این تصمیم به نعمت‌های موجود توجه کنید و با قدردانی پیش بروید.',
                isPositive: true
            },
            {
                surah: 'النحل',
                ayahNumber: '۹۷',
                text: 'مَنْ عَمِلَ صَالِحًا مِّن ذَكَرٍ أَوْ أُنثَىٰ وَهُوَ مُؤْمِنٌ فَلَنُحْيِيَنَّهُ حَيَاةً طَيِّبَةً',
                translation: 'هر کس عمل صالح انجام دهد، مرد یا زن، در حالی که مؤمن باشد، زندگی پاکیزه به او عطا خواهیم کرد',
                interpretation: 'عمل شما باید با نیت خالصانه و ایمان همراه باشد. اگر این کار را با نیت خیر انجام دهید، به زندگی بهتری دست خواهید یافت.',
                isPositive: true
            },
            {
                surah: 'الطلاق',
                ayahNumber: '۳',
                text: 'وَمَن يَتَوَكَّلْ عَلَى اللَّهِ فَهُوَ حَسْبُهُ',
                translation: 'و هر کس بر خدا توکل کند، خدا او را کافی است',
                interpretation: 'توکل به خدا کلید موفقیت شماست. با اعتماد به خداوند و تلاش خود، این کار را انجام دهید.',
                isPositive: true
            },
            {
                surah: 'البقره',
                ayahNumber: '۲۱۶',
                text: 'وَعَسَىٰ أَن تَكْرَهُوا شَيْئًا وَهُوَ خَيْرٌ لَّكُمْ',
                translation: 'و شاید چیزی را ناخوش دارید در حالی که برای شما خیر است',
                interpretation: 'گاهی چیزی که در ظاهر ناخوشایند است، در باطن خیر شماست. با تفکر عمیق و مشورت تصمیم بگیرید.',
                isPositive: true
            },
            {
                surah: 'آل عمران',
                ayahNumber: '۱۵۹',
                text: 'فَإِذَا عَزَمْتَ فَتَوَكَّلْ عَلَى اللَّهِ',
                translation: 'پس هنگامی که تصمیم گرفتی، بر خدا توکل کن',
                interpretation: 'زمان تصمیم‌گیری فرا رسیده است. با توکل به خدا و اعتماد به نفس، قدم بردارید.',
                isPositive: true
            }
        ];

        // انتخاب تصادفی یک آیه
        this.selectedAyah = ayahs[Math.floor(Math.random() * ayahs.length)];

        // نمایش نتیجه
        this.showResult();
    }

    showResult() {
        this.goToStep(4);

        const resultIcon = document.getElementById('resultIcon');
        const resultTitle = document.getElementById('resultTitle');
        const surahName = document.getElementById('surahName');
        const ayahNumber = document.getElementById('ayahNumber');
        const ayahText = document.getElementById('ayahText');
        const ayahTranslation = document.getElementById('ayahTranslation');
        const interpretationText = document.getElementById('interpretationText');

        // Set result icon
        if (this.selectedAyah.isPositive) {
            resultIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
            resultIcon.classList.remove('negative');
            resultTitle.textContent = 'نتیجه استخاره مثبت است';
        } else {
            resultIcon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
            resultIcon.classList.add('negative');
            resultTitle.textContent = 'نتیجه استخاره منفی است';
        }

        // Set ayah details
        surahName.textContent = `سوره ${this.selectedAyah.surah}`;
        ayahNumber.textContent = `آیه ${this.selectedAyah.ayahNumber}`;
        ayahText.textContent = this.selectedAyah.text;
        ayahTranslation.textContent = this.selectedAyah.translation;
        interpretationText.textContent = this.selectedAyah.interpretation;

        // Save to history (localStorage)
        this.saveToHistory();
    }

    saveToHistory() {
        const history = JSON.parse(localStorage.getItem('estekharaHistory') || '[]');
        
        const record = {
            date: new Date().toISOString(),
            question: this.userQuestion,
            ayah: this.selectedAyah,
            timestamp: Date.now()
        };

        history.unshift(record);
        
        // Keep only last 10 records
        if (history.length > 10) {
            history.splice(10);
        }

        localStorage.setItem('estekharaHistory', JSON.stringify(history));
    }

    shareResult() {
        const text = `استخاره با قرآن کریم
        
سوال: ${this.userQuestion}

${this.selectedAyah.surah} - آیه ${this.selectedAyah.ayahNumber}
${this.selectedAyah.translation}

از اپلیکیشن محبوب`;

        if (navigator.share) {
            navigator.share({
                title: 'نتیجه استخاره',
                text: text
            }).catch(err => console.log('Error sharing:', err));
        } else {
            // Fallback: کپی به کلیپبورد
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('متن کپی شد');
            });
        }
    }

    resetEstekhara() {
        this.currentStep = 1;
        this.userQuestion = '';
        this.selectedAyah = null;
        
        // Clear input
        const questionInput = document.getElementById('questionInput');
        if (questionInput) questionInput.value = '';

        // Go to first step
        this.goToStep(1);
    }

    showNotification(message) {
        const notification = document.createElement('div');
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
            max-width: 90%;
            text-align: center;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2500);
    }
}

// Animations
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
    window.estekhara = new Estekhara();
});